import sqlite3
from typing import Any


class BaseRepository:
    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db

    @staticmethod
    def _row(r: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(r) if r else None

    @staticmethod
    def _rows(rs: list[sqlite3.Row]) -> list[dict[str, Any]]:
        return [dict(r) for r in rs]
