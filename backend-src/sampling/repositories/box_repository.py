from typing import Any

from sampling.repositories.base import BaseRepository


class BoxRepository(BaseRepository):
    def list_all(self) -> list[dict[str, Any]]:
        return self._rows(
            self.db.execute("""
            SELECT b.*, l.name AS location_name, COUNT(t.id) AS tube_count
            FROM boxes b
            LEFT JOIN locations l ON l.id = b.location_id
            LEFT JOIN tubes t ON t.box_id = b.id
            GROUP BY b.id ORDER BY b.created_at DESC
        """).fetchall()
        )

    def get_by_id(self, box_id: int) -> dict[str, Any] | None:
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

    def get_with_tubes(self, box_id: int) -> dict[str, Any] | None:
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

    def get_by_barcode(self, barcode: str) -> dict[str, Any] | None:
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

    def create(
        self,
        barcode: str,
        name: str | None = None,
        location_id: int | None = None,
        notes: str | None = None,
        changed_by: int | None = None,
    ) -> dict[str, Any]:
        cur = self.db.execute(
            "INSERT INTO boxes (barcode, name, location_id, notes) VALUES (?,?,?,?)",
            (barcode, name, location_id, notes),
        )
        row_id = cur.lastrowid
        if row_id is None:  # pragma: no cover
            raise RuntimeError("INSERT returned no row ID")
        box = self.get_by_id(row_id)
        if box is None:  # pragma: no cover
            raise RuntimeError(f"Row {row_id} not found after INSERT")
        self._record_history(box, changed_by)
        return box

    def update(
        self,
        box_id: int,
        barcode: str,
        name: str | None = None,
        location_id: int | None = None,
        notes: str | None = None,
        changed_by: int | None = None,
    ) -> dict[str, Any] | None:
        self.db.execute(
            "UPDATE boxes SET barcode=?, name=?, location_id=?, notes=?,"
            " updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (barcode, name, location_id, notes, box_id),
        )
        box = self.get_by_id(box_id)
        if box is not None:
            self._record_history(box, changed_by)
        return box

    def get_history(self, box_id: int) -> list[dict[str, Any]]:
        return self._rows(
            self.db.execute(
                """
            SELECT bh.*, u.username AS changed_by_username, l.name AS location_name
            FROM box_history bh
            LEFT JOIN users u ON u.id = bh.changed_by
            LEFT JOIN locations l ON l.id = bh.location_id
            WHERE bh.box_id = ?
            ORDER BY bh.changed_at DESC, bh.id DESC
        """,
                (box_id,),
            ).fetchall()
        )

    def revert(
        self,
        box_id: int,
        version_id: int,
        changed_by: int | None = None,
    ) -> dict[str, Any] | None:
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

    def _record_history(self, box: dict[str, Any], changed_by: int | None) -> None:
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

    def empty(self, box_id: int) -> None:
        self.db.execute("UPDATE tubes SET box_id=NULL WHERE box_id=?", (box_id,))

    def delete(self, box_id: int) -> bool:
        return self.db.execute("DELETE FROM boxes WHERE id=?", (box_id,)).rowcount > 0

    def search(self, query: str) -> list[dict[str, Any]]:
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

    def export_flat(
        self, box_id: int | None = None, ids: list[int] | None = None
    ) -> list[dict[str, Any]]:
        if box_id is not None:
            where, params = "WHERE b.id = ?", (box_id,)
        elif ids is not None:
            if not ids:
                return []
            where, params = f"WHERE b.id IN ({','.join('?' * len(ids))})", tuple(ids)
        else:
            where, params = "", ()
        return self._rows(
            self.db.execute(
                f"""
            SELECT b.id, b.barcode, b.name, l.name AS location, b.notes,
                   COUNT(t.id) AS tube_count, b.created_at
            FROM boxes b
            LEFT JOIN locations l ON l.id = b.location_id
            LEFT JOIN tubes t ON t.box_id = b.id
            {where}
            GROUP BY b.id ORDER BY b.created_at DESC
        """,
                params,
            ).fetchall()
        )

    def export_tubes_for_boxes(self, box_ids: list[int]) -> list[dict[str, Any]]:
        if not box_ids:
            return []
        placeholders = ",".join("?" * len(box_ids))
        return self._rows(
            self.db.execute(
                f"""
            SELECT box_id, barcode, sample_date, site_name, latitude, longitude,
                   sample_type, description, volume_ml, weight_g, depth_cm,
                   created_at, updated_at
            FROM tubes WHERE box_id IN ({placeholders})
            ORDER BY depth_cm ASC, created_at ASC
        """,
                tuple(box_ids),
            ).fetchall()
        )
