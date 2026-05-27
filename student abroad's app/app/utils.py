from functools import wraps
from flask import flash, redirect, session, url_for
from .i18n import get_translator


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash(get_translator()("login_required"))
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
