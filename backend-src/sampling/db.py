import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get(
    "DB_PATH", str(Path(__file__).parent.parent.parent / "data" / "samples.db")
)
_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db


def run_migrations():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version    TEXT     PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        applied = {r[0] for r in db.execute("SELECT version FROM schema_migrations").fetchall()}

        # Bootstrap: if tables exist from before migrations were introduced, mark 001 as applied.
        existing = {
            r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        if "boxes" in existing and "001_initial" not in applied:
            db.execute("INSERT INTO schema_migrations (version) VALUES (?)", ("001_initial",))
            applied.add("001_initial")

    for path in sorted(_MIGRATIONS_DIR.glob("*.sql")):
        version = path.stem
        if version in applied:
            continue
        with get_db() as db:
            db.executescript(path.read_text())
            db.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
        print(f"  [migration] applied {version}")
