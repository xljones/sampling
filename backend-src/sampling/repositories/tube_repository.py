class TubeRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self):
        return self._rows(self.db.execute("""
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode,
                   l.name AS box_location_name
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            LEFT JOIN locations l ON l.id = b.location_id
            ORDER BY t.created_at DESC
        """).fetchall())

    def get_by_id(self, tube_id):
        return self._row(self.db.execute("""
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode,
                   l.name AS box_location_name
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            LEFT JOIN locations l ON l.id = b.location_id
            WHERE t.id=?
        """, (tube_id,)).fetchone())

    def get_by_barcode(self, barcode):
        return self._row(self.db.execute("""
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode,
                   l.name AS box_location_name
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            LEFT JOIN locations l ON l.id = b.location_id
            WHERE t.barcode=?
        """, (barcode,)).fetchone())

    def create(self, barcode, box_id=None, collection_date=None, site_name=None,
               latitude=None, longitude=None, sample_type=None, description=None,
               volume_ml=None, weight_g=None, depth_cm=None, changed_by=None):
        cur = self.db.execute("""
            INSERT INTO tubes (barcode, box_id, collection_date, site_name, latitude, longitude,
                sample_type, description, volume_ml, weight_g, depth_cm)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (barcode, box_id, collection_date, site_name, latitude, longitude,
              sample_type, description, volume_ml, weight_g, depth_cm))
        tube = self.get_by_id(cur.lastrowid)
        self._record_history(tube, changed_by)
        return tube

    def update(self, tube_id, barcode, box_id=None, collection_date=None, site_name=None,
               latitude=None, longitude=None, sample_type=None, description=None,
               volume_ml=None, weight_g=None, depth_cm=None, changed_by=None):
        self.db.execute("""
            UPDATE tubes
            SET barcode=?, box_id=?, collection_date=?, site_name=?, latitude=?,
                longitude=?, sample_type=?, description=?, volume_ml=?, weight_g=?,
                depth_cm=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (barcode, box_id, collection_date, site_name, latitude, longitude,
              sample_type, description, volume_ml, weight_g, depth_cm, tube_id))
        tube = self.get_by_id(tube_id)
        self._record_history(tube, changed_by)
        return tube

    def get_history(self, tube_id):
        return self._rows(self.db.execute("""
            SELECT th.*, u.username AS changed_by_username, b.barcode AS box_barcode
            FROM tube_history th
            LEFT JOIN users u ON u.id = th.changed_by
            LEFT JOIN boxes b ON b.id = th.box_id
            WHERE th.tube_id = ?
            ORDER BY th.changed_at DESC
        """, (tube_id,)).fetchall())

    def revert(self, tube_id, version_id, changed_by=None):
        h = self._row(self.db.execute(
            "SELECT * FROM tube_history WHERE id=? AND tube_id=?", (version_id, tube_id)
        ).fetchone())
        if not h:
            return None
        return self.update(
            tube_id, h["barcode"], box_id=h["box_id"],
            collection_date=h["collection_date"], site_name=h["site_name"],
            latitude=h["latitude"], longitude=h["longitude"],
            sample_type=h["sample_type"], description=h["description"],
            volume_ml=h["volume_ml"], weight_g=h["weight_g"], depth_cm=h["depth_cm"],
            changed_by=changed_by,
        )

    def _record_history(self, tube, changed_by):
        self.db.execute("""
            INSERT INTO tube_history
                (tube_id, changed_by, barcode, box_id, collection_date, site_name,
                 latitude, longitude, sample_type, description, volume_ml, weight_g, depth_cm)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (tube["id"], changed_by, tube["barcode"], tube.get("box_id"),
              tube.get("collection_date"), tube.get("site_name"),
              tube.get("latitude"), tube.get("longitude"),
              tube.get("sample_type"), tube.get("description"),
              tube.get("volume_ml"), tube.get("weight_g"), tube.get("depth_cm")))

    def bulk_assign(self, tube_ids, box_id, changed_by=None):
        if not tube_ids:
            return 0
        placeholders = ','.join('?' * len(tube_ids))
        self.db.execute(
            f"UPDATE tubes SET box_id=?, updated_at=CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
            [box_id] + list(tube_ids),
        )
        for tube_id in tube_ids:
            tube = self.get_by_id(tube_id)
            if tube:
                self._record_history(tube, changed_by)
        return len(tube_ids)

    def delete(self, tube_id):
        return self.db.execute("DELETE FROM tubes WHERE id=?", (tube_id,)).rowcount > 0

    def search(self, query):
        q = f"%{query}%"
        return self._rows(self.db.execute(
            "SELECT *, 'tube' AS type FROM tubes"
            " WHERE barcode LIKE ? OR site_name LIKE ? OR sample_type LIKE ?"
            " OR description LIKE ? LIMIT 10",
            (q, q, q, q),
        ).fetchall())

    def export_all(self):
        return self._rows(self.db.execute("""
            SELECT t.barcode, b.barcode AS box_barcode, b.name AS box_name,
                   t.collection_date, t.site_name, t.latitude, t.longitude,
                   t.sample_type, t.description, t.volume_ml, t.weight_g, t.depth_cm,
                   t.created_at, t.updated_at
            FROM tubes t LEFT JOIN boxes b ON b.id = t.box_id
            ORDER BY t.created_at DESC
        """).fetchall())

    @staticmethod
    def _row(r):
        return dict(r) if r else None

    @staticmethod
    def _rows(rs):
        return [dict(r) for r in rs]
