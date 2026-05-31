from typing import Any

from sampling.repositories.base import BaseRepository


class CoreRepository(BaseRepository):
    def list_all(self) -> list[dict[str, Any]]:
        return self._rows(
            self.db.execute("""
            SELECT c.*, l.name AS location_name,
                   COUNT(t.id) AS tube_count,
                   COUNT(DISTINCT CASE WHEN t.box_id IS NOT NULL THEN t.box_id END) AS box_count
            FROM cores c
            LEFT JOIN locations l ON l.id = c.location_id
            LEFT JOIN tubes t ON t.core_id = c.id
            GROUP BY c.id ORDER BY c.created_at DESC
        """).fetchall()
        )

    def get_by_id(self, core_id: int) -> dict[str, Any] | None:
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

    def get_with_tubes(self, core_id: int) -> dict[str, Any] | None:
        core = self.get_by_id(core_id)
        if not core:
            return None
        core["tubes"] = self._rows(
            self.db.execute(
                """
                SELECT t.*, b.barcode AS box_barcode, b.name AS box_name
                FROM tubes t LEFT JOIN boxes b ON b.id = t.box_id
                WHERE t.core_id=? ORDER BY t.depth_cm ASC, t.created_at ASC
                """,
                (core_id,),
            ).fetchall()
        )
        return core

    def get_by_barcode(self, barcode: str) -> dict[str, Any] | None:
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
        barcode: str,
        name: str | None = None,
        location_id: int | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        site_name: str | None = None,
        collection_date: str | None = None,
        depth_cm: float | None = None,
        collector: str | None = None,
        sample_type: str | None = None,
        owner: str | None = None,
        notes: str | None = None,
        changed_by: int | None = None,
    ) -> dict[str, Any]:
        cur = self.db.execute(
            """
            INSERT INTO cores (barcode, name, location_id, latitude, longitude,
                site_name, collection_date, depth_cm, collector, sample_type, owner, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            (
                barcode,
                name,
                location_id,
                latitude,
                longitude,
                site_name,
                collection_date,
                depth_cm,
                collector,
                sample_type,
                owner,
                notes,
            ),
        )
        row_id = cur.lastrowid
        if row_id is None:  # pragma: no cover
            raise RuntimeError("INSERT returned no row ID")
        core = self.get_by_id(row_id)
        if core is None:  # pragma: no cover
            raise RuntimeError(f"Row {row_id} not found after INSERT")
        self._record_history(core, changed_by)
        return core

    def update(
        self,
        core_id: int,
        barcode: str,
        name: str | None = None,
        location_id: int | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        site_name: str | None = None,
        collection_date: str | None = None,
        depth_cm: float | None = None,
        collector: str | None = None,
        sample_type: str | None = None,
        owner: str | None = None,
        notes: str | None = None,
        changed_by: int | None = None,
    ) -> dict[str, Any] | None:
        self.db.execute(
            """
            UPDATE cores
            SET barcode=?, name=?, location_id=?, latitude=?, longitude=?,
                site_name=?, collection_date=?, depth_cm=?, collector=?,
                sample_type=?, owner=?, notes=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """,
            (
                barcode,
                name,
                location_id,
                latitude,
                longitude,
                site_name,
                collection_date,
                depth_cm,
                collector,
                sample_type,
                owner,
                notes,
                core_id,
            ),
        )
        core = self.get_by_id(core_id)
        if core is not None:
            self._record_history(core, changed_by)
        return core

    def get_history(self, core_id: int) -> list[dict[str, Any]]:
        return self._rows(
            self.db.execute(
                """
            SELECT ch.*, u.username AS changed_by_username, l.name AS location_name
            FROM core_history ch
            LEFT JOIN users u ON u.id = ch.changed_by
            LEFT JOIN locations l ON l.id = ch.location_id
            WHERE ch.core_id = ?
            ORDER BY ch.changed_at DESC, ch.id DESC
        """,
                (core_id,),
            ).fetchall()
        )

    def revert(
        self,
        core_id: int,
        version_id: int,
        changed_by: int | None = None,
    ) -> dict[str, Any] | None:
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

    def _record_history(self, core: dict[str, Any], changed_by: int | None) -> None:
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

    def delete(self, core_id: int) -> bool:
        return self.db.execute("DELETE FROM cores WHERE id=?", (core_id,)).rowcount > 0

    def search(self, query: str) -> list[dict[str, Any]]:
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
