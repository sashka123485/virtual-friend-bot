import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("DATABASE_FILE", Path(__file__).resolve().parent / "dialogues.sqlite3"))


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, id)"
    )
    conn.commit()
    return conn


def init_db():
    conn = connect()
    conn.close()


def get_history(user_id: int):
    conn = connect()
    rows = conn.execute(
        "SELECT role, text FROM messages WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def add_message(user_id: int, role: str, text: str):
    conn = connect()
    conn.execute(
        "INSERT INTO messages(user_id, role, text) VALUES (?, ?, ?)",
        (user_id, role, text),
    )
    conn.commit()
    conn.close()


def clear_history(user_id: int):
    conn = connect()
    conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
