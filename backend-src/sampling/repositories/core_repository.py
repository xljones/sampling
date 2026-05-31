from collections import defaultdict
from typing import Any

from sampling.repositories.base import BaseRepository


class CoreRepository(BaseRepository):
    FLAT_FIELDS: list[str] = [
        "barcode",
        "name",
        "location",
        "site_name",
        "latitude",
        "longitude",
        "collection_date",
        "depth_cm",
        "collector",
        "sample_type",
        "owner",
        "notes",
        "tube_count",
        "box_count",
        "created_at",
        "updated_at",
    ]
    WITH_TUBES_FIELDS: list[str] = [
        "row_type",
        "core_barcode",
        "core_name",
        "core_location",
        "core_site_name",
        "core_latitude",
        "core_longitude",
        "core_collection_date",
        "core_depth_cm",
        "core_collector",
        "core_sample_type",
        "core_owner",
        "core_notes",
        "core_tube_count",
        "core_box_count",
        "core_created_at",
        "core_updated_at",
        "box_barcode",
        "box_name",
        "tube_barcode",
        "tube_sample_date",
        "tube_site_name",
        "tube_latitude",
        "tube_longitude",
        "tube_sample_type",
        "tube_description",
        "tube_volume_ml",
        "tube_weight_g",
        "tube_depth_cm",
        "tube_created_at",
        "tube_updated_at",
    ]

    def list_all(self) -> list[dict[str, Any]]:
        """Return all cores with location name, tube count, and box count, newest first."""
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
        """Return a core by primary key, including location name, or None if not found."""
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
        """Return a core with its tubes list (with box info), or None if not found."""
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
        """Return a core by its barcode, including location name, or None if not found."""
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
        """Insert a new core and record its initial history snapshot; return the created core."""
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
        """Update core fields, record a history snapshot, and return the updated core."""
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
        """Return full audit history for a core, newest first, with username and location."""
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
        """Restore a core from a history record; return None if the record doesn't exist."""
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
        """Write a snapshot of the core's current field values to core_history."""
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
        """Delete a core by its primary key; return True if a row was removed."""
        return self.db.execute("DELETE FROM cores WHERE id=?", (core_id,)).rowcount > 0

    def search(self, query: str) -> list[dict[str, Any]]:
        """Return up to 10 cores whose barcode, name, or site name matches the query substring."""
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

    def export_flat(
        self, core_id: int | None = None, ids: list[int] | None = None
    ) -> list[dict[str, Any]]:
        """Return flat export rows for cores, optionally filtered by core_id or id list."""
        where: str
        params: tuple
        if core_id is not None:
            where, params = "WHERE c.id = ?", (core_id,)
        elif ids is not None:
            if not ids:
                return []
            where, params = f"WHERE c.id IN ({','.join('?' * len(ids))})", tuple(ids)
        else:
            where, params = "", ()
        return self._rows(
            self.db.execute(
                f"""
            SELECT c.id, c.barcode, c.name, l.name AS location, c.site_name,
                   c.latitude, c.longitude, c.collection_date, c.depth_cm,
                   c.collector, c.sample_type, c.owner, c.notes,
                   COUNT(t.id) AS tube_count,
                   COUNT(DISTINCT CASE WHEN t.box_id IS NOT NULL THEN t.box_id END) AS box_count,
                   c.created_at, c.updated_at
            FROM cores c
            LEFT JOIN locations l ON l.id = c.location_id
            LEFT JOIN tubes t ON t.core_id = c.id
            {where}
            GROUP BY c.id ORDER BY c.created_at DESC
        """,
                params,
            ).fetchall()
        )

    def export_tubes_for_cores(self, core_ids: list[int]) -> list[dict[str, Any]]:
        """Return tubes for the given core IDs with box info joined, ordered by box then depth."""
        if not core_ids:  # pragma: no cover
            return []
        placeholders = ",".join("?" * len(core_ids))
        return self._rows(
            self.db.execute(
                f"""
            SELECT t.core_id, t.box_id, b.barcode AS box_barcode, b.name AS box_name,
                   t.barcode, t.sample_date, t.site_name, t.latitude, t.longitude,
                   t.sample_type, t.description, t.volume_ml, t.weight_g, t.depth_cm,
                   t.created_at, t.updated_at
            FROM tubes t
            LEFT JOIN boxes b ON b.id = t.box_id
            WHERE t.core_id IN ({placeholders})
            ORDER BY CASE WHEN t.box_id IS NULL THEN 1 ELSE 0 END,
                     t.box_id, t.depth_cm ASC, t.created_at ASC
        """,
                tuple(core_ids),
            ).fetchall()
        )

    def build_with_tubes_rows(
        self, core_id: int | None = None, ids: list[int] | None = None
    ) -> list[dict[str, Any]]:
        """Return hierarchical export rows (core header, box header, tube rows) for CSV/TSV."""
        cores = self.export_flat(core_id=core_id, ids=ids)
        if not cores:
            return []
        tubes = self.export_tubes_for_cores([c["id"] for c in cores])
        tubes_by_core: dict[int, list] = defaultdict(list)
        for t in tubes:
            tubes_by_core[t["core_id"]].append(t)
        _null: dict[str, Any] = {f: None for f in self.WITH_TUBES_FIELDS}
        result = []
        for core in cores:
            row = dict(_null)
            row.update(
                row_type="core",
                core_barcode=core["barcode"],
                core_name=core["name"],
                core_location=core["location"],
                core_site_name=core["site_name"],
                core_latitude=core["latitude"],
                core_longitude=core["longitude"],
                core_collection_date=core["collection_date"],
                core_depth_cm=core["depth_cm"],
                core_collector=core["collector"],
                core_sample_type=core["sample_type"],
                core_owner=core["owner"],
                core_notes=core["notes"],
                core_tube_count=core["tube_count"],
                core_box_count=core["box_count"],
                core_created_at=core["created_at"],
                core_updated_at=core["updated_at"],
            )
            result.append(row)
            by_box: dict[int | None, list] = {}
            for t in tubes_by_core[core["id"]]:
                key = t["box_id"]
                if key not in by_box:
                    by_box[key] = []
                by_box[key].append(t)
            for box_id_key, box_tubes in by_box.items():
                first = box_tubes[0]
                if box_id_key is not None:
                    row = dict(_null)
                    row.update(
                        row_type="box",
                        core_barcode=core["barcode"],
                        box_barcode=first["box_barcode"],
                        box_name=first["box_name"],
                    )
                    result.append(row)
                for t in box_tubes:
                    row = dict(_null)
                    row.update(
                        row_type="tube",
                        core_barcode=core["barcode"],
                        box_barcode=t["box_barcode"],
                        tube_barcode=t["barcode"],
                        tube_sample_date=t["sample_date"],
                        tube_site_name=t["site_name"],
                        tube_latitude=t["latitude"],
                        tube_longitude=t["longitude"],
                        tube_sample_type=t["sample_type"],
                        tube_description=t["description"],
                        tube_volume_ml=t["volume_ml"],
                        tube_weight_g=t["weight_g"],
                        tube_depth_cm=t["depth_cm"],
                        tube_created_at=t["created_at"],
                        tube_updated_at=t["updated_at"],
                    )
                    result.append(row)
        return result

    def build_json(
        self, core_id: int | None = None, ids: list[int] | None = None
    ) -> list[dict[str, Any]]:
        """Return nested JSON export structure: each core with its boxes and unboxed tubes."""
        cores = self.export_flat(core_id=core_id, ids=ids)
        if not cores:
            return []
        tubes = self.export_tubes_for_cores([c["id"] for c in cores])
        tubes_by_core: dict[int, list] = defaultdict(list)
        for t in tubes:
            tubes_by_core[t["core_id"]].append(t)
        result = []
        for core in cores:
            by_box: dict[int | None, dict] = {}
            for t in tubes_by_core[core["id"]]:
                key = t["box_id"]
                if key not in by_box:
                    by_box[key] = {"barcode": t["box_barcode"], "name": t["box_name"], "tubes": []}
                by_box[key]["tubes"].append(
                    {
                        "barcode": t["barcode"],
                        "sample_date": t["sample_date"],
                        "site_name": t["site_name"],
                        "latitude": t["latitude"],
                        "longitude": t["longitude"],
                        "sample_type": t["sample_type"],
                        "description": t["description"],
                        "volume_ml": t["volume_ml"],
                        "weight_g": t["weight_g"],
                        "depth_cm": t["depth_cm"],
                        "created_at": t["created_at"],
                        "updated_at": t["updated_at"],
                    }
                )
            result.append(
                {
                    "barcode": core["barcode"],
                    "name": core["name"],
                    "location": core["location"],
                    "site_name": core["site_name"],
                    "latitude": core["latitude"],
                    "longitude": core["longitude"],
                    "collection_date": core["collection_date"],
                    "depth_cm": core["depth_cm"],
                    "collector": core["collector"],
                    "sample_type": core["sample_type"],
                    "owner": core["owner"],
                    "notes": core["notes"],
                    "tube_count": core["tube_count"],
                    "box_count": core["box_count"],
                    "created_at": core["created_at"],
                    "updated_at": core["updated_at"],
                    "boxes": [v for k, v in by_box.items() if k is not None],
                    "unboxed_tubes": by_box[None]["tubes"] if None in by_box else [],
                }
            )
        return result
