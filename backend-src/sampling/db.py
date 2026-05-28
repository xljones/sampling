import os
import sqlite3
from pathlib import Path

_DEFAULT_DB_PATH = str(Path(__file__).parent.parent.parent / "data" / "samples.db")
_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_db():
    db_path = os.environ.get("DB_PATH", _DEFAULT_DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = sqlite3.connect(db_path)
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

        # Bootstrap: detect migrations applied before schema_migrations tracking was introduced.
        tables = {
            r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        def col(table, column):
            return any(
                r[1] == column
                for r in db.execute(f"PRAGMA table_info({table})").fetchall()
            )

        checks = [
            ("001_initial",      "boxes" in tables),
            ("002_add_users",    "users" in tables),
            ("003_boxes_updated_at", "boxes" in tables and col("boxes", "updated_at")),
            ("004_version_history",  "box_history" in tables),
            ("005_locations",    "locations" in tables),
            ("006_readonly_users", "users" in tables and col("users", "is_readonly")),
        ]
        for version, already_exists in checks:
            if already_exists and version not in applied:
                db.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
                applied.add(version)

    for path in sorted(_MIGRATIONS_DIR.glob("*.sql")):
        version = path.stem
        if version in applied:
            continue
        with get_db() as db:
            db.executescript(path.read_text())
            db.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
        print(f"  [migration] applied {version}")
