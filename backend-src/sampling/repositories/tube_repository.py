class TubeRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self):
        return self._rows(self.db.execute("""
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode
            FROM tubes t LEFT JOIN boxes b ON b.id = t.box_id
            ORDER BY t.created_at DESC
        """).fetchall())

    def get_by_id(self, tube_id):
        return self._row(self.db.execute("""
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode
            FROM tubes t LEFT JOIN boxes b ON b.id = t.box_id
            WHERE t.id=?
        """, (tube_id,)).fetchone())

    def get_by_barcode(self, barcode):
        return self._row(self.db.execute("""
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode
            FROM tubes t LEFT JOIN boxes b ON b.id = t.box_id
            WHERE t.barcode=?
        """, (barcode,)).fetchone())

    def create(self, barcode, box_id=None, collection_date=None, site_name=None,
               latitude=None, longitude=None, sample_type=None, description=None,
               volume_ml=None, weight_g=None, depth_cm=None):
        cur = self.db.execute("""
            INSERT INTO tubes (barcode, box_id, collection_date, site_name, latitude, longitude,
                sample_type, description, volume_ml, weight_g, depth_cm)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (barcode, box_id, collection_date, site_name, latitude, longitude,
              sample_type, description, volume_ml, weight_g, depth_cm))
        return self.get_by_id(cur.lastrowid)

    def update(self, tube_id, barcode, box_id=None, collection_date=None, site_name=None,
               latitude=None, longitude=None, sample_type=None, description=None,
               volume_ml=None, weight_g=None, depth_cm=None):
        self.db.execute("""
            UPDATE tubes
            SET barcode=?, box_id=?, collection_date=?, site_name=?, latitude=?,
                longitude=?, sample_type=?, description=?, volume_ml=?, weight_g=?,
                depth_cm=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (barcode, box_id, collection_date, site_name, latitude, longitude,
              sample_type, description, volume_ml, weight_g, depth_cm, tube_id))
        return self.get_by_id(tube_id)

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
