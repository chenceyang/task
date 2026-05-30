from flask import Blueprint, render_template
from ..db import get_db

news_bp = Blueprint("news", __name__, url_prefix="/news")


@news_bp.route("/")
def index():
    db = get_db()
    items = db.execute(
        "SELECT title, summary, source, category, news_date FROM news ORDER BY news_date DESC, id DESC"
    ).fetchall()
    return render_template("news.html", items=items)
