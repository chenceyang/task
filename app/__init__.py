from pathlib import Path
from flask import Flask, g, session
from .db import close_db, get_db, init_db
from .i18n import LANGUAGES, current_language, get_translator
from .vocab.routes import weather_bp



def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    instance_dir = Path(__file__).resolve().parent / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)

    app.config.update(
        SECRET_KEY="change-this-secret-key",
        DATABASE=str(instance_dir / "app.sqlite3"),
    )

    app.teardown_appcontext(close_db)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .memo.routes import memo_bp
    from .news.routes import news_bp
    from .vocab.routes import vocab_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(memo_bp)
    app.register_blueprint(vocab_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(news_bp)

    with app.app_context():
        init_db()

    @app.context_processor
    def inject_globals():
        user = None
        db = get_db()
        user_id = session.get("user_id")
        if user_id:
            user = db.execute(
                "SELECT id, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

        latest_news = db.execute(
            "SELECT id, title, summary, source, category, news_date "
            "FROM news ORDER BY news_date DESC, id DESC LIMIT 1"
        ).fetchone()

        return {
            "t": get_translator(),
            "lang": current_language(),
            "languages": LANGUAGES,
            "user": user,
            "latest_news": latest_news,
        }

    return app
