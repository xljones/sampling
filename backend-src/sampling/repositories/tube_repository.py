from typing import Any

from sampling.repositories.base import BaseRepository


class TubeRepository(BaseRepository):
    EXPORT_FIELDS: list[str] = [
        "barcode",
        "box_barcode",
        "box_name",
        "sample_date",
        "site_name",
        "latitude",
        "longitude",
        "sample_type",
        "description",
        "volume_ml",
        "weight_g",
        "depth_cm",
        "created_at",
        "updated_at",
    ]

    def list_all(self) -> list[dict[str, Any]]:
        """Return all tubes with joined box, location, and core fields, newest first."""
        return self._rows(
            self.db.execute("""
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode,
                   l.name AS box_location_name,
                   c.barcode AS core_barcode, c.name AS core_name, cl.name AS core_location_name,
                   c.site_name AS core_site_name, c.latitude AS core_latitude,
                   c.longitude AS core_longitude, c.collection_date AS core_collection_date,
                   c.sample_type AS core_sample_type, c.depth_cm AS core_total_depth
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            LEFT JOIN locations l ON l.id = b.location_id
            LEFT JOIN cores c ON c.id = t.core_id
            LEFT JOIN locations cl ON cl.id = c.location_id
            ORDER BY t.created_at DESC
        """).fetchall()
        )

    def get_by_id(self, tube_id: int) -> dict[str, Any] | None:
        """Return a tube by primary key with joined box, location, and core fields, or None."""
        return self._row(
            self.db.execute(
                """
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode,
                   l.name AS box_location_name,
                   c.barcode AS core_barcode, c.name AS core_name, cl.name AS core_location_name,
                   c.site_name AS core_site_name, c.latitude AS core_latitude,
                   c.longitude AS core_longitude, c.collection_date AS core_collection_date,
                   c.sample_type AS core_sample_type, c.depth_cm AS core_total_depth
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            LEFT JOIN locations l ON l.id = b.location_id
            LEFT JOIN cores c ON c.id = t.core_id
            LEFT JOIN locations cl ON cl.id = c.location_id
            WHERE t.id=?
        """,
                (tube_id,),
            ).fetchone()
        )

    def get_by_barcode(self, barcode: str) -> dict[str, Any] | None:
        """Return a tube by barcode with joined box, location, and core fields, or None."""
        return self._row(
            self.db.execute(
                """
            SELECT t.*, b.name AS box_name, b.barcode AS box_barcode,
                   l.name AS box_location_name,
                   c.barcode AS core_barcode, c.name AS core_name, cl.name AS core_location_name,
                   c.site_name AS core_site_name, c.latitude AS core_latitude,
                   c.longitude AS core_longitude, c.collection_date AS core_collection_date,
                   c.sample_type AS core_sample_type, c.depth_cm AS core_total_depth
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            LEFT JOIN locations l ON l.id = b.location_id
            LEFT JOIN cores c ON c.id = t.core_id
            LEFT JOIN locations cl ON cl.id = c.location_id
            WHERE t.barcode=?
        """,
                (barcode,),
            ).fetchone()
        )

    def create(
        self,
        barcode: str,
        box_id: int | None = None,
        core_id: int | None = None,
        sample_date: str | None = None,
        site_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        sample_type: str | None = None,
        description: str | None = None,
        volume_ml: float | None = None,
        weight_g: float | None = None,
        depth_cm: float | None = None,
        changed_by: int | None = None,
    ) -> dict[str, Any]:
        """Insert a new tube, record initial history, and return it with joined fields."""
        cur = self.db.execute(
            """
            INSERT INTO tubes (
                barcode, box_id, core_id, sample_date, site_name, latitude, longitude,
                sample_type, description, volume_ml, weight_g, depth_cm)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            (
                barcode,
                box_id,
                core_id,
                sample_date,
                site_name,
                latitude,
                longitude,
                sample_type,
                description,
                volume_ml,
                weight_g,
                depth_cm,
            ),
        )
        row_id = cur.lastrowid
        if row_id is None:  # pragma: no cover
            raise RuntimeError("INSERT returned no row ID")
        tube = self.get_by_id(row_id)
        if tube is None:  # pragma: no cover
            raise RuntimeError(f"Row {row_id} not found after INSERT")
        self._record_history(tube, changed_by)
        return tube

    def update(
        self,
        tube_id: int,
        barcode: str,
        box_id: int | None = None,
        core_id: int | None = None,
        sample_date: str | None = None,
        site_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        sample_type: str | None = None,
        description: str | None = None,
        volume_ml: float | None = None,
        weight_g: float | None = None,
        depth_cm: float | None = None,
        changed_by: int | None = None,
    ) -> dict[str, Any] | None:
        """Update tube fields, record a history snapshot, and return the updated tube."""
        self.db.execute(
            """
            UPDATE tubes
            SET barcode=?, box_id=?, core_id=?, sample_date=?, site_name=?, latitude=?,
                longitude=?, sample_type=?, description=?, volume_ml=?, weight_g=?,
                depth_cm=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """,
            (
                barcode,
                box_id,
                core_id,
                sample_date,
                site_name,
                latitude,
                longitude,
                sample_type,
                description,
                volume_ml,
                weight_g,
                depth_cm,
                tube_id,
            ),
        )
        tube = self.get_by_id(tube_id)
        if tube is not None:
            self._record_history(tube, changed_by)
        return tube

    def get_history(self, tube_id: int) -> list[dict[str, Any]]:
        """Return full audit history for a tube, newest first, with username and barcodes."""
        return self._rows(
            self.db.execute(
                """
            SELECT th.*, u.username AS changed_by_username,
                   b.barcode AS box_barcode, c.barcode AS core_barcode
            FROM tube_history th
            LEFT JOIN users u ON u.id = th.changed_by
            LEFT JOIN boxes b ON b.id = th.box_id
            LEFT JOIN cores c ON c.id = th.core_id
            WHERE th.tube_id = ?
            ORDER BY th.changed_at DESC, th.id DESC
        """,
                (tube_id,),
            ).fetchall()
        )

    def revert(
        self,
        tube_id: int,
        version_id: int,
        changed_by: int | None = None,
    ) -> dict[str, Any] | None:
        """Restore a tube from a history record; return None if the record doesn't exist."""
        h = self._row(
            self.db.execute(
                "SELECT * FROM tube_history WHERE id=? AND tube_id=?", (version_id, tube_id)
            ).fetchone()
        )
        if not h:
            return None
        return self.update(
            tube_id,
            h["barcode"],
            box_id=h["box_id"],
            core_id=h["core_id"],
            sample_date=h["sample_date"],
            site_name=h["site_name"],
            latitude=h["latitude"],
            longitude=h["longitude"],
            sample_type=h["sample_type"],
            description=h["description"],
            volume_ml=h["volume_ml"],
            weight_g=h["weight_g"],
            depth_cm=h["depth_cm"],
            changed_by=changed_by,
        )

    def _record_history(self, tube: dict[str, Any], changed_by: int | None) -> None:
        """Write a snapshot of the tube's current field values to tube_history."""
        self.db.execute(
            """
            INSERT INTO tube_history
                (tube_id, changed_by, barcode, box_id, core_id, sample_date, site_name,
                 latitude, longitude, sample_type, description, volume_ml, weight_g, depth_cm)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            (
                tube["id"],
                changed_by,
                tube["barcode"],
                tube.get("box_id"),
                tube.get("core_id"),
                tube.get("sample_date"),
                tube.get("site_name"),
                tube.get("latitude"),
                tube.get("longitude"),
                tube.get("sample_type"),
                tube.get("description"),
                tube.get("volume_ml"),
                tube.get("weight_g"),
                tube.get("depth_cm"),
            ),
        )

    def bulk_assign(
        self,
        tube_ids: list[int],
        box_id: int,
        changed_by: int | None = None,
    ) -> int:
        """Bulk-assign tubes to a box, record history for each, and return the count."""
        if not tube_ids:  # pragma: no cover
            return 0
        placeholders = ",".join("?" * len(tube_ids))
        self.db.execute(
            f"UPDATE tubes SET box_id=?, updated_at=CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
            [box_id] + list(tube_ids),
        )
        for tube_id in tube_ids:
            tube = self.get_by_id(tube_id)
            if tube:
                self._record_history(tube, changed_by)
        return len(tube_ids)

    def delete(self, tube_id: int) -> bool:
        """Delete a tube by its primary key; return True if a row was removed."""
        return self.db.execute("DELETE FROM tubes WHERE id=?", (tube_id,)).rowcount > 0

    def search(self, query: str) -> list[dict[str, Any]]:
        """Return up to 10 tubes matching the query against barcode, site, or sample type."""
        q = f"%{query}%"
        return self._rows(
            self.db.execute(
                "SELECT *, 'tube' AS type FROM tubes"
                " WHERE barcode LIKE ? OR site_name LIKE ? OR sample_type LIKE ?"
                " OR description LIKE ? LIMIT 10",
                (q, q, q, q),
            ).fetchall()
        )

    def export_all(self) -> list[dict[str, Any]]:
        """Return all tubes for export with joined box and core fields, newest first."""
        return self._rows(
            self.db.execute("""
            SELECT t.barcode, b.barcode AS box_barcode, b.name AS box_name,
                   c.barcode AS core_barcode, c.name AS core_name, cl.name AS core_location_name,
                   c.site_name AS core_site_name, c.latitude AS core_latitude,
                   c.longitude AS core_longitude, c.collection_date AS core_collection_date,
                   c.sample_type AS core_sample_type, c.depth_cm AS core_total_depth,
                   t.sample_date, t.site_name, t.latitude, t.longitude,
                   t.sample_type, t.description, t.volume_ml, t.weight_g, t.depth_cm,
                   t.created_at, t.updated_at
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            LEFT JOIN cores c ON c.id = t.core_id
            LEFT JOIN locations cl ON cl.id = c.location_id
            ORDER BY t.created_at DESC
        """).fetchall()
        )
