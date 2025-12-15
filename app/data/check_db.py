import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = (PROJECT_ROOT / "app_db.sqlite3").resolve()

print("Using database at:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("\nTables:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

if not tables:
    print("No tables found")
else:
    for row in tables:
        print("-", row[0])

print("\nSessions:")
try:
    cur.execute("SELECT id, created_at, user_notes FROM sessions ORDER BY id DESC LIMIT 10")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print("Error reading sessions:", e)

conn.close()
