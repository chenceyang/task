from flask import Blueprint, redirect, render_template, request, session, url_for
from ..db import get_db
from ..i18n import LANGUAGES

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    db = get_db()
    stats = {
        "memo_count": 0,
        "vocab_count": 0,
        "news_count": db.execute("SELECT COUNT(*) FROM news").fetchone()[0],
    }

    user_id = session.get("user_id")
    if user_id:
        stats["memo_count"] = db.execute(
            "SELECT COUNT(*) FROM memos WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]
        stats["vocab_count"] = db.execute(
            "SELECT COUNT(*) FROM vocab WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]

    return render_template("home.html", stats=stats)


@main_bp.route("/lang/<lang_code>")
def set_language(lang_code):
    if lang_code in LANGUAGES:
        session["lang"] = lang_code
    return redirect(request.referrer or url_for("main.home"))
