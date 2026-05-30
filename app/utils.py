from functools import wraps
from flask import flash, redirect, session, url_for
from .i18n import get_translator
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash(get_translator()("login_required"))
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


API_KEY = os.getenv("API_KEY")
url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric"

response = requests.get(url)

data = response.json()

print(data)
