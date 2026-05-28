class LocationRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self):
        return self._rows(
            self.db.execute("""
            SELECT l.*, COUNT(b.id) AS box_count
            FROM locations l LEFT JOIN boxes b ON b.location_id = l.id
            GROUP BY l.id ORDER BY l.name
        """).fetchall()
        )

    def get_by_id(self, loc_id):
        r = self.db.execute("SELECT * FROM locations WHERE id=?", (loc_id,)).fetchone()
        return dict(r) if r else None

    def get_with_boxes(self, loc_id):
        loc = self.get_by_id(loc_id)
        if not loc:
            return None
        loc["boxes"] = self._rows(
            self.db.execute(
                """
            SELECT b.*, COUNT(t.id) AS tube_count
            FROM boxes b LEFT JOIN tubes t ON t.box_id = b.id
            WHERE b.location_id = ?
            GROUP BY b.id ORDER BY b.name ASC, b.barcode ASC
        """,
                (loc_id,),
            ).fetchall()
        )
        return loc

    def create(self, name):
        cur = self.db.execute("INSERT INTO locations (name) VALUES (?)", (name,))
        return self.get_by_id(cur.lastrowid)

    def update(self, loc_id, name):
        self.db.execute("UPDATE locations SET name=? WHERE id=?", (name, loc_id))
        return self.get_by_id(loc_id)

    def delete(self, loc_id):
        count = self.db.execute(
            "SELECT COUNT(*) FROM boxes WHERE location_id=?", (loc_id,)
        ).fetchone()[0]
        if count > 0:
            return (
                False,
                f"Cannot delete: {count} box{'es' if count != 1 else ''} use this location",
            )
        self.db.execute("UPDATE box_history SET location_id=NULL WHERE location_id=?", (loc_id,))
        self.db.execute("DELETE FROM locations WHERE id=?", (loc_id,))
        return True, None

    @staticmethod
    def _row(r):
        return dict(r) if r else None

    @staticmethod
    def _rows(rs):
        return [dict(r) for r in rs]
