from typing import Any

from sampling.repositories.base import BaseRepository


class LocationRepository(BaseRepository):

    def list_all(self) -> list[dict[str, Any]]:
        return self._rows(
            self.db.execute("""
            SELECT l.*, COUNT(b.id) AS box_count
            FROM locations l LEFT JOIN boxes b ON b.location_id = l.id
            GROUP BY l.id ORDER BY l.name
        """).fetchall()
        )

    def get_by_id(self, loc_id: int) -> dict[str, Any] | None:
        r = self.db.execute("SELECT * FROM locations WHERE id=?", (loc_id,)).fetchone()
        return dict(r) if r else None

    def get_with_boxes(self, loc_id: int) -> dict[str, Any] | None:
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

    def create(self, name: str) -> dict[str, Any]:
        cur = self.db.execute("INSERT INTO locations (name) VALUES (?)", (name,))
        row_id = cur.lastrowid
        if row_id is None:
            raise RuntimeError("INSERT returned no row ID")
        loc = self.get_by_id(row_id)
        if loc is None:
            raise RuntimeError(f"Row {row_id} not found after INSERT")
        return loc

    def update(self, loc_id: int, name: str) -> dict[str, Any] | None:
        self.db.execute("UPDATE locations SET name=? WHERE id=?", (name, loc_id))
        return self.get_by_id(loc_id)

    def delete(self, loc_id: int) -> tuple[bool, str | None]:
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
