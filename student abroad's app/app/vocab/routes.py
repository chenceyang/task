from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..db import get_db
from ..i18n import get_translator
from ..utils import login_required
from flask import Blueprint, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

weather_bp = Blueprint("weather", __name__)

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


vocab_bp = Blueprint("vocab", __name__, url_prefix="/vocab")


def rank_entries(entries, query):
    if not entries:
        return []

    texts = [f"{row['term']} {row['meaning']}" for row in entries]
    try:
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(texts + [query])
        scores = cosine_similarity(matrix[:-1], matrix[-1]).ravel()
        ranked = sorted(zip(entries, scores), key=lambda x: x[1], reverse=True)
        return [row for row, _ in ranked]
    except Exception:
        lowered = query.lower()
        ranked = sorted(
            entries,
            key=lambda row: (
                lowered in f"{row['term']} {row['meaning']}".lower(),
                len(row["term"]),
            ),
            reverse=True,
        )
        return ranked


@vocab_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    t = get_translator()
    db = get_db()
    user_id = session.get("user_id")

    if request.method == "POST":
        term = request.form.get("term", "").strip()
        meaning = request.form.get("meaning", "").strip()
        lang_from = request.form.get("lang_from", "ko").strip() or "ko"
        lang_to = request.form.get("lang_to", "zh").strip() or "zh"

        if term and meaning:
            db.execute(
                "INSERT INTO vocab (user_id, term, meaning, lang_from, lang_to) VALUES (?, ?, ?, ?, ?)",
                (user_id, term, meaning, lang_from, lang_to),
            )
            db.commit()
            flash(t("vocab_saved"))
            return redirect(url_for("vocab.index"))

    entries = db.execute(
        "SELECT id, term, meaning, lang_from, lang_to, created_at FROM vocab WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()

    query = request.args.get("q", "").strip()
    results = rank_entries(entries, query) if query else entries

    return render_template("vocab/index.html", entries=entries, results=results, query=query)


@vocab_bp.route("/delete/<int:vocab_id>", methods=["POST"])
@login_required
def delete(vocab_id):
    t = get_translator()
    db = get_db()
    user_id = session.get("user_id")
    db.execute("DELETE FROM vocab WHERE id = ? AND user_id = ?", (vocab_id, user_id))
    db.commit()
    flash(t("vocab_deleted"))
    return redirect(url_for("vocab.index"))
