import json
from app.data.db import get_connection


def get_session(session_id: int) -> dict | None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, created_at, user_notes, answers_json FROM sessions WHERE id = ?",
            (session_id,),
        )
        row = cur.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "created_at": row[1],
            "user_notes": row[2] or "",
            "answers": json.loads(row[3]),
        }


def get_results_for_session(session_id: int) -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT symptom, probable_causes_json, next_tests_json
            FROM results
            WHERE session_id = ?
            """,
            (session_id,),
        )
        rows = cur.fetchall()

        results = []
        for symptom, causes_json, tests_json in rows:
            results.append(
                {
                    "symptom": symptom,
                    "probable_causes": json.loads(causes_json),
                    "next_tests": json.loads(tests_json),
                }
            )
        return results
