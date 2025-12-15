import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Project root = two levels up from app/data/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "app_db.sqlite3"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_notes TEXT,
            answers_json TEXT NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            symptom TEXT NOT NULL,
            probable_causes_json TEXT NOT NULL,
            next_tests_json TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
        """)

        conn.commit()


def save_session(user_notes: str, answers: dict) -> int:
    created_at = datetime.utcnow().isoformat()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sessions (created_at, user_notes, answers_json) VALUES (?, ?, ?)",
            (created_at, user_notes, json.dumps(answers)),
        )
        session_id = cur.lastrowid
        conn.commit()
        return session_id


def save_results(session_id: int, results: list[dict]) -> None:
    with get_connection() as conn:
        cur = conn.cursor()

        for r in results:
            cur.execute(
                """
                INSERT INTO results (session_id, symptom, probable_causes_json, next_tests_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    r["symptom"],
                    json.dumps(r["probable_causes"]),
                    json.dumps(r["next_tests"]),
                ),
            )

        conn.commit()
