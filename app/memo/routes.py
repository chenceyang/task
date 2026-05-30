from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from ..db import get_db
from ..i18n import get_translator
from ..utils import login_required

memo_bp = Blueprint("memo", __name__, url_prefix="/memo")


@memo_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    t = get_translator()
    db = get_db()
    user_id = session.get("user_id")

    if request.method == "POST":
        event = request.form.get("event", "").strip()
        note = request.form.get("note", "").strip()
        event_time = request.form.get("event_time", "").strip()

        if event and event_time:
            db.execute(
                "INSERT INTO memos (user_id, event, note, event_time) VALUES (?, ?, ?, ?)",
                (user_id, event, note, event_time),
            )
            db.commit()
            flash(t("memo_saved"))
            return redirect(url_for("memo.index"))

    memos = db.execute(
        "SELECT id, event, note, event_time, created_at FROM memos WHERE user_id = ? ORDER BY event_time DESC, id DESC",
        (user_id,),
    ).fetchall()
    return render_template("memo/index.html", memos=memos)


@memo_bp.route("/delete/<int:memo_id>", methods=["POST"])
@login_required
def delete(memo_id):
    t = get_translator()
    db = get_db()
    user_id = session.get("user_id")
    db.execute("DELETE FROM memos WHERE id = ? AND user_id = ?", (memo_id, user_id))
    db.commit()
    flash(t("memo_deleted"))
    return redirect(url_for("memo.index"))
