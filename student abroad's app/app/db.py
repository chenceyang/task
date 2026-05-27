import sqlite3
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    pw_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event TEXT NOT NULL,
    note TEXT,
    event_time TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vocab (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    term TEXT NOT NULL,
    meaning TEXT NOT NULL,
    lang_from TEXT NOT NULL DEFAULT 'ko',
    lang_to TEXT NOT NULL DEFAULT 'zh',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    news_date TEXT NOT NULL
);
"""


SEED_NEWS = [
    ("교통 소식", "일부 지하철 노선이 주말에 점검될 예정입니다.", "City Transit", "교통", "2026-05-22"),
    ("생활 정보", "주변 마트와 편의점 할인 정보가 갱신되었습니다.", "Local News", "생활", "2026-05-22"),
    ("캠퍼스 안내", "이번 주 도서관과 학생센터 운영 시간이 업데이트되었습니다.", "Campus Office", "캠퍼스", "2026-05-22"),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    count = db.execute("SELECT COUNT(*) FROM news").fetchone()[0]
    if count == 0:
        db.executemany(
            "INSERT INTO news (title, summary, source, category, news_date) VALUES (?, ?, ?, ?, ?)",
            SEED_NEWS,
        )
    db.commit()
