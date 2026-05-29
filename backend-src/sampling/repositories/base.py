class BaseRepository:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def _row(r):
        return dict(r) if r else None

    @staticmethod
    def _rows(rs):
        return [dict(r) for r in rs]
