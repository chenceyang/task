from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from ..db import get_db
from ..i18n import get_translator

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    t = get_translator()
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["pw_hash"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            return redirect(url_for("main.home"))

        flash(t("login_error"))
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    t = get_translator()
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not email or not password or not confirm:
            flash(t("fill_required"))
            return render_template("auth/register.html")

        if password != confirm:
            flash(t("password_mismatch"))
            return render_template("auth/register.html")

        db = get_db()
        exists = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if exists:
            flash(t("register_exists"))
            return render_template("auth/register.html")

        db.execute(
            "INSERT INTO users (email, pw_hash) VALUES (?, ?)",
            (email, generate_password_hash(password)),
        )
        db.commit()
        flash(t("register_success"))
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    t = get_translator()
    lang = session.get("lang", "ko")
    session.clear()
    session["lang"] = lang
    flash(t("logout_success"))
    return redirect(url_for("main.home"))
