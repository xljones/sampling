class BoxRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self):
        return self._rows(self.db.execute("""
            SELECT b.*, COUNT(t.id) AS tube_count
            FROM boxes b LEFT JOIN tubes t ON t.box_id = b.id
            GROUP BY b.id ORDER BY b.created_at DESC
        """).fetchall())

    def get_by_id(self, box_id):
        return self._row(self.db.execute(
            "SELECT * FROM boxes WHERE id=?", (box_id,)
        ).fetchone())

    def get_with_tubes(self, box_id):
        box = self.get_by_id(box_id)
        if not box:
            return None
        box["tubes"] = self._rows(self.db.execute(
            "SELECT * FROM tubes WHERE box_id=? ORDER BY depth_cm ASC, created_at ASC",
            (box_id,),
        ).fetchall())
        return box

    def get_by_barcode(self, barcode):
        return self._row(self.db.execute(
            "SELECT * FROM boxes WHERE barcode=?", (barcode,)
        ).fetchone())

    def create(self, barcode, name=None, location=None, notes=None):
        cur = self.db.execute(
            "INSERT INTO boxes (barcode, name, location, notes) VALUES (?,?,?,?)",
            (barcode, name, location, notes),
        )
        return self.get_by_id(cur.lastrowid)

    def update(self, box_id, barcode, name=None, location=None, notes=None):
        self.db.execute(
            "UPDATE boxes SET barcode=?, name=?, location=?, notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (barcode, name, location, notes, box_id),
        )
        return self.get_by_id(box_id)

    def delete(self, box_id):
        return self.db.execute("DELETE FROM boxes WHERE id=?", (box_id,)).rowcount > 0

    def search(self, query):
        q = f"%{query}%"
        return self._rows(self.db.execute(
            "SELECT *, 'box' AS type FROM boxes"
            " WHERE barcode LIKE ? OR name LIKE ? OR location LIKE ? LIMIT 10",
            (q, q, q),
        ).fetchall())

    def export_all(self):
        return self._rows(self.db.execute("""
            SELECT b.barcode, b.name, b.location, b.notes,
                   COUNT(t.id) AS tube_count, b.created_at
            FROM boxes b LEFT JOIN tubes t ON t.box_id = b.id
            GROUP BY b.id ORDER BY b.created_at DESC
        """).fetchall())

    @staticmethod
    def _row(r):
        return dict(r) if r else None

    @staticmethod
    def _rows(rs):
        return [dict(r) for r in rs]
