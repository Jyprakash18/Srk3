import sqlite3
from config import DB_PATH


def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            affiliate_tag TEXT,
            autopost INTEGER DEFAULT 0,
            channel_id TEXT
        )
        """)


def create_user(user_id: int):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))


def set_tag(user_id: int, tag: str):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("UPDATE users SET affiliate_tag=? WHERE user_id=?", (tag, user_id))


def set_autopost(user_id: int, status: bool):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("UPDATE users SET autopost=? WHERE user_id=?", (1 if status else 0, user_id))


def set_channel(user_id: int, channel_id: str):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("UPDATE users SET channel_id=? WHERE user_id=?", (channel_id, user_id))


def get_user(user_id: int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(
            "SELECT affiliate_tag, autopost, channel_id FROM users WHERE user_id=?",
            (user_id,)
        )
        return cur.fetchone()
