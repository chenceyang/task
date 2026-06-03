from flask import Blueprint, flash, redirect, render_template, request, session, url_for, jsonify
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

import numpy as np
import json
import requests
import os

from ..db import get_db
from ..i18n import get_translator
from ..utils import login_required

# AI embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Convert text -> embedding vector
def text_to_embedding(text):
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


# Convert stored JSON -> numpy array
def embedding_to_array(embedding_text):
    return np.array(json.loads(embedding_text))


weather_bp = Blueprint("weather", __name__)
vocab_bp = Blueprint("vocab", __name__, url_prefix="/vocab")


@weather_bp.route("/weather", methods=["GET"])
def weather():

    API_KEY = os.getenv("API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric"

    response = requests.get(url)

    data = response.json()

    return jsonify({
        "city": data["name"],
        "temp": data["main"]["temp"],
        "weather": data["weather"][0]["main"]
    })


# Vector similarity search
def rank_entries(entries, query):

    if not entries or not query:
        return entries

    try:
        query_vec = np.array(text_to_embedding(query)).reshape(1, -1)

        scored = []

        for row in entries:

            if row["embedding"]:

                row_vec = embedding_to_array(
                    row["embedding"]
                ).reshape(1, -1)

                score = cosine_similarity(
                    query_vec,
                    row_vec
                )[0][0]

            else:
                score = 0

            scored.append((row, score))

        scored.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return [row for row, _ in scored]

    except Exception:
        lowered = query.lower()

        return sorted(
            entries,
            key=lambda row: lowered in (
                f"{row['term']} {row['meaning']}".lower()
            ),
            reverse=True,
        )


@vocab_bp.route("/", methods=["GET", "POST"])
@login_required
def index():

    t = get_translator()

    db = get_db()

    user_id = session.get("user_id")

    # Save vocab
    if request.method == "POST":

        term = request.form.get("term", "").strip()

        meaning = request.form.get("meaning", "").strip()

        lang_from = request.form.get(
            "lang_from",
            "ko"
        ).strip() or "ko"

        lang_to = request.form.get(
            "lang_to",
            "zh"
        ).strip() or "zh"

        if term and meaning:

            text = f"{term} {meaning}"

            embedding = text_to_embedding(text)

            db.execute(
                """
                INSERT INTO vocab
                (
                    user_id,
                    term,
                    meaning,
                    lang_from,
                    lang_to,
                    embedding
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    term,
                    meaning,
                    lang_from,
                    lang_to,
                    json.dumps(embedding),
                ),
            )

            db.commit()

            flash(t("vocab_saved"))

            return redirect(url_for("vocab.index"))

    # Load vocab list
    entries = db.execute(
        """
        SELECT
            id,
            term,
            meaning,
            lang_from,
            lang_to,
            embedding,
            created_at
        FROM vocab
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    ).fetchall()

    # Search
    query = request.args.get("q", "").strip()

    results = (
        rank_entries(entries, query)
        if query
        else entries
    )

    return render_template(
        "vocab/index.html",
        entries=entries,
        results=results,
        query=query,
    )


@vocab_bp.route("/delete/<int:vocab_id>", methods=["POST"])
@login_required
def delete(vocab_id):

    t = get_translator()

    db = get_db()

    user_id = session.get("user_id")

    db.execute(
        "DELETE FROM vocab WHERE id = ? AND user_id = ?",
        (vocab_id, user_id)
    )

    db.commit()

    flash(t("vocab_deleted"))

    return redirect(url_for("vocab.index"))
