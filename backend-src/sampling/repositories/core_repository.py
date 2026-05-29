from sampling.repositories.base import BaseRepository


class CoreRepository(BaseRepository):

    def list_all(self):
        return self._rows(
            self.db.execute("""
            SELECT c.*, l.name AS location_name, COUNT(t.id) AS tube_count
            FROM cores c
            LEFT JOIN locations l ON l.id = c.location_id
            LEFT JOIN tubes t ON t.core_id = c.id
            GROUP BY c.id ORDER BY c.created_at DESC
        """).fetchall()
        )

    def get_by_id(self, core_id):
        return self._row(
            self.db.execute(
                """
            SELECT c.*, l.name AS location_name
            FROM cores c LEFT JOIN locations l ON l.id = c.location_id
            WHERE c.id=?
        """,
                (core_id,),
            ).fetchone()
        )

    def get_with_tubes(self, core_id):
        core = self.get_by_id(core_id)
        if not core:
            return None
        core["tubes"] = self._rows(
            self.db.execute(
                "SELECT * FROM tubes WHERE core_id=? ORDER BY depth_cm ASC, created_at ASC",
                (core_id,),
            ).fetchall()
        )
        return core

    def get_by_barcode(self, barcode):
        return self._row(
            self.db.execute(
                """
            SELECT c.*, l.name AS location_name
            FROM cores c LEFT JOIN locations l ON l.id = c.location_id
            WHERE c.barcode=?
        """,
                (barcode,),
            ).fetchone()
        )

    def create(
        self,
        barcode,
        name=None,
        location_id=None,
        latitude=None,
        longitude=None,
        site_name=None,
        collection_date=None,
        depth_cm=None,
        collector=None,
        sample_type=None,
        owner=None,
        notes=None,
        changed_by=None,
    ):
        cur = self.db.execute(
            """
            INSERT INTO cores (barcode, name, location_id, latitude, longitude,
                site_name, collection_date, depth_cm, collector, sample_type, owner, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            (
                barcode, name, location_id, latitude, longitude,
                site_name, collection_date, depth_cm, collector, sample_type, owner, notes,
            ),
        )
        core = self.get_by_id(cur.lastrowid)
        self._record_history(core, changed_by)
        return core

    def update(
        self,
        core_id,
        barcode,
        name=None,
        location_id=None,
        latitude=None,
        longitude=None,
        site_name=None,
        collection_date=None,
        depth_cm=None,
        collector=None,
        sample_type=None,
        owner=None,
        notes=None,
        changed_by=None,
    ):
        self.db.execute(
            """
            UPDATE cores
            SET barcode=?, name=?, location_id=?, latitude=?, longitude=?,
                site_name=?, collection_date=?, depth_cm=?, collector=?,
                sample_type=?, owner=?, notes=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """,
            (
                barcode, name, location_id, latitude, longitude,
                site_name, collection_date, depth_cm, collector, sample_type, owner, notes,
                core_id,
            ),
        )
        core = self.get_by_id(core_id)
        self._record_history(core, changed_by)
        return core

    def get_history(self, core_id):
        return self._rows(
            self.db.execute(
                """
            SELECT ch.*, u.username AS changed_by_username, l.name AS location_name
            FROM core_history ch
            LEFT JOIN users u ON u.id = ch.changed_by
            LEFT JOIN locations l ON l.id = ch.location_id
            WHERE ch.core_id = ?
            ORDER BY ch.changed_at DESC
        """,
                (core_id,),
            ).fetchall()
        )

    def revert(self, core_id, version_id, changed_by=None):
        h = self._row(
            self.db.execute(
                "SELECT * FROM core_history WHERE id=? AND core_id=?", (version_id, core_id)
            ).fetchone()
        )
        if not h:
            return None
        return self.update(
            core_id,
            h["barcode"],
            name=h["name"],
            location_id=h["location_id"],
            latitude=h["latitude"],
            longitude=h["longitude"],
            site_name=h["site_name"],
            collection_date=h["collection_date"],
            depth_cm=h["depth_cm"],
            collector=h["collector"],
            sample_type=h["sample_type"],
            owner=h["owner"],
            notes=h["notes"],
            changed_by=changed_by,
        )

    def _record_history(self, core, changed_by):
        self.db.execute(
            """
            INSERT INTO core_history
                (core_id, changed_by, barcode, name, location_id, latitude, longitude,
                 site_name, collection_date, depth_cm, collector, sample_type, owner, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            (
                core["id"],
                changed_by,
                core["barcode"],
                core.get("name"),
                core.get("location_id"),
                core.get("latitude"),
                core.get("longitude"),
                core.get("site_name"),
                core.get("collection_date"),
                core.get("depth_cm"),
                core.get("collector"),
                core.get("sample_type"),
                core.get("owner"),
                core.get("notes"),
            ),
        )

    def delete(self, core_id):
        return self.db.execute("DELETE FROM cores WHERE id=?", (core_id,)).rowcount > 0

    def search(self, query):
        q = f"%{query}%"
        return self._rows(
            self.db.execute(
                """
            SELECT c.*, l.name AS location_name, 'core' AS type
            FROM cores c LEFT JOIN locations l ON l.id = c.location_id
            WHERE c.barcode LIKE ? OR c.name LIKE ? OR c.site_name LIKE ?
            LIMIT 10
        """,
                (q, q, q),
            ).fetchall()
        )

