class BoxRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self):
        return self._rows(
            self.db.execute("""
            SELECT b.*, l.name AS location_name, COUNT(t.id) AS tube_count
            FROM boxes b
            LEFT JOIN locations l ON l.id = b.location_id
            LEFT JOIN tubes t ON t.box_id = b.id
            GROUP BY b.id ORDER BY b.created_at DESC
        """).fetchall()
        )

    def get_by_id(self, box_id):
        return self._row(
            self.db.execute(
                """
            SELECT b.*, l.name AS location_name
            FROM boxes b LEFT JOIN locations l ON l.id = b.location_id
            WHERE b.id=?
        """,
                (box_id,),
            ).fetchone()
        )

    def get_with_tubes(self, box_id):
        box = self.get_by_id(box_id)
        if not box:
            return None
        box["tubes"] = self._rows(
            self.db.execute(
                "SELECT * FROM tubes WHERE box_id=? ORDER BY depth_cm ASC, created_at ASC",
                (box_id,),
            ).fetchall()
        )
        return box

    def get_by_barcode(self, barcode):
        return self._row(
            self.db.execute(
                """
            SELECT b.*, l.name AS location_name
            FROM boxes b LEFT JOIN locations l ON l.id = b.location_id
            WHERE b.barcode=?
        """,
                (barcode,),
            ).fetchone()
        )

    def create(self, barcode, name=None, location_id=None, notes=None, changed_by=None):
        cur = self.db.execute(
            "INSERT INTO boxes (barcode, name, location_id, notes) VALUES (?,?,?,?)",
            (barcode, name, location_id, notes),
        )
        box = self.get_by_id(cur.lastrowid)
        self._record_history(box, changed_by)
        return box

    def update(self, box_id, barcode, name=None, location_id=None, notes=None, changed_by=None):
        self.db.execute(
            "UPDATE boxes SET barcode=?, name=?, location_id=?, notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (barcode, name, location_id, notes, box_id),
        )
        box = self.get_by_id(box_id)
        self._record_history(box, changed_by)
        return box

    def get_history(self, box_id):
        return self._rows(
            self.db.execute(
                """
            SELECT bh.*, u.username AS changed_by_username, l.name AS location_name
            FROM box_history bh
            LEFT JOIN users u ON u.id = bh.changed_by
            LEFT JOIN locations l ON l.id = bh.location_id
            WHERE bh.box_id = ?
            ORDER BY bh.changed_at DESC
        """,
                (box_id,),
            ).fetchall()
        )

    def revert(self, box_id, version_id, changed_by=None):
        h = self._row(
            self.db.execute(
                "SELECT * FROM box_history WHERE id=? AND box_id=?", (version_id, box_id)
            ).fetchone()
        )
        if not h:
            return None
        return self.update(
            box_id,
            h["barcode"],
            name=h["name"],
            location_id=h["location_id"],
            notes=h["notes"],
            changed_by=changed_by,
        )

    def _record_history(self, box, changed_by):
        self.db.execute(
            """
            INSERT INTO box_history (box_id, changed_by, barcode, name, location_id, notes)
            VALUES (?,?,?,?,?,?)
        """,
            (
                box["id"],
                changed_by,
                box["barcode"],
                box.get("name"),
                box.get("location_id"),
                box.get("notes"),
            ),
        )

    def empty(self, box_id):
        self.db.execute("UPDATE tubes SET box_id=NULL WHERE box_id=?", (box_id,))

    def delete(self, box_id):
        return self.db.execute("DELETE FROM boxes WHERE id=?", (box_id,)).rowcount > 0

    def search(self, query):
        q = f"%{query}%"
        return self._rows(
            self.db.execute(
                """
            SELECT b.*, l.name AS location_name, 'box' AS type
            FROM boxes b LEFT JOIN locations l ON l.id = b.location_id
            WHERE b.barcode LIKE ? OR b.name LIKE ? OR l.name LIKE ?
            LIMIT 10
        """,
                (q, q, q),
            ).fetchall()
        )

    def export_all(self):
        return self._rows(
            self.db.execute("""
            SELECT b.barcode, b.name, l.name AS location, b.notes,
                   COUNT(t.id) AS tube_count, b.created_at
            FROM boxes b
            LEFT JOIN locations l ON l.id = b.location_id
            LEFT JOIN tubes t ON t.box_id = b.id
            GROUP BY b.id ORDER BY b.created_at DESC
        """).fetchall()
        )

    @staticmethod
    def _row(r):
        return dict(r) if r else None

    @staticmethod
    def _rows(rs):
        return [dict(r) for r in rs]
