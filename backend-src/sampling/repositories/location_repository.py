from typing import Any

from sampling.repositories.base import BaseRepository


class LocationRepository(BaseRepository):
    def list_all(self) -> list[dict[str, Any]]:
        """Return all locations with their box and core counts, ordered alphabetically by name."""
        return self._rows(
            self.db.execute("""
            SELECT l.*,
                (SELECT COUNT(*) FROM boxes b WHERE b.location_id = l.id) AS box_count,
                (SELECT COUNT(*) FROM cores c WHERE c.location_id = l.id) AS core_count
            FROM locations l
            ORDER BY l.name
        """).fetchall()
        )

    def get_by_id(self, loc_id: int) -> dict[str, Any] | None:
        """Return a single location by its primary key, or None if not found."""
        r = self.db.execute("SELECT * FROM locations WHERE id=?", (loc_id,)).fetchone()
        return dict(r) if r else None

    def get_with_items(self, loc_id: int) -> dict[str, Any] | None:
        """Return a location with its boxes and cores lists, or None if not found."""
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
        loc["cores"] = self._rows(
            self.db.execute(
                """
            SELECT c.id, c.barcode, c.name, c.notes, COUNT(t.id) AS tube_count
            FROM cores c LEFT JOIN tubes t ON t.core_id = c.id
            WHERE c.location_id = ?
            GROUP BY c.id ORDER BY c.name ASC, c.barcode ASC
        """,
                (loc_id,),
            ).fetchall()
        )
        return loc

    def create(self, name: str) -> dict[str, Any]:
        """Insert a new location with the given name and return the created record."""
        cur = self.db.execute("INSERT INTO locations (name) VALUES (?)", (name,))
        row_id = cur.lastrowid
        if row_id is None:  # pragma: no cover
            raise RuntimeError("INSERT returned no row ID")
        loc = self.get_by_id(row_id)
        if loc is None:  # pragma: no cover
            raise RuntimeError(f"Row {row_id} not found after INSERT")
        return loc

    def update(self, loc_id: int, name: str) -> dict[str, Any] | None:
        """Rename a location and return the updated record, or None if not found."""
        self.db.execute("UPDATE locations SET name=? WHERE id=?", (name, loc_id))
        return self.get_by_id(loc_id)

    def delete(self, loc_id: int) -> tuple[bool, str | None]:
        """Delete a location; return (False, msg) if boxes reference it, else (True, None)."""
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
