import csv
import io
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, Response, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.tube_repository import TubeRepository

bp = Blueprint("export", __name__)

_TUBE_FIELDS = [
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

_BOX_WITH_TUBES_FIELDS = [
    "row_type",
    "box_barcode",
    "box_name",
    "box_location",
    "box_notes",
    "box_tube_count",
    "box_created_at",
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

_CORE_WITH_TUBES_FIELDS = [
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

_BOX_FIELDS = [
    "barcode",
    "name",
    "location",
    "notes",
    "tube_count",
    "created_at",
]

_CORE_FIELDS = [
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


@bp.get("/api/export/tubes")
@login_required
def export_tubes() -> Response:
    fmt = request.args.get("format", "csv")
    with get_db() as db:
        data = TubeRepository(db).export_all()
    if fmt == "json":
        return _json_response([{f: r.get(f) for f in _TUBE_FIELDS} for r in data], "tubes")
    return _respond(data, _TUBE_FIELDS, "tubes")


@bp.get("/api/export/boxes")
@login_required
def export_boxes() -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    ids = _parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        if fmt == "json":
            if flat:
                rows: list[dict[str, Any]] = [{f: r.get(f) for f in _BOX_FIELDS} for r in _build_box_rows(db, ids=ids)]
            else:
                rows = _build_box_json(db, ids=ids)
            return _json_response(rows, "boxes-flat" if flat else "boxes")
        if flat:
            return _respond(_build_box_rows(db, ids=ids), _BOX_FIELDS, "boxes-flat")
        return _respond(_build_box_with_tubes_rows(db, ids=ids), _BOX_WITH_TUBES_FIELDS, "boxes")


@bp.get("/api/export/boxes/<int:box_id>")
@login_required
def export_box(box_id: int) -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    with get_db() as db:
        if fmt == "json":
            if flat:
                data = _build_box_rows(db, box_id=box_id)
                label = _safe(data[0]["barcode"]) if data else "box"
                return _json_response([{f: r.get(f) for f in _BOX_FIELDS} for r in data], f"box-flat-{label}")
            rows = _build_box_json(db, box_id=box_id)
            label = _safe(rows[0]["barcode"]) if rows else "box"
            return _json_response(rows, f"box-{label}")
        if flat:
            data = _build_box_rows(db, box_id=box_id)
            label = _safe(data[0]["barcode"]) if data else "box"
            return _respond(data, _BOX_FIELDS, f"box-flat-{label}")
        data = _build_box_with_tubes_rows(db, box_id=box_id)
        label = _safe(data[0]["box_barcode"]) if data else "box"
        return _respond(data, _BOX_WITH_TUBES_FIELDS, f"box-{label}")


@bp.get("/api/export/cores")
@login_required
def export_cores() -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    ids = _parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        if fmt == "json":
            if flat:
                rows = [{f: r.get(f) for f in _CORE_FIELDS} for r in _build_core_rows(db, ids=ids)]
            else:
                rows = _build_core_json(db, ids=ids)
            return _json_response(rows, "cores-flat" if flat else "cores")
        if flat:
            return _respond(_build_core_rows(db, ids=ids), _CORE_FIELDS, "cores-flat")
        return _respond(_build_core_with_tubes_rows(db, ids=ids), _CORE_WITH_TUBES_FIELDS, "cores")


@bp.get("/api/export/cores/<int:core_id>")
@login_required
def export_core(core_id: int) -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    with get_db() as db:
        if fmt == "json":
            if flat:
                data = _build_core_rows(db, core_id=core_id)
                label = _safe(data[0]["barcode"]) if data else "core"
                return _json_response([{f: r.get(f) for f in _CORE_FIELDS} for r in data], f"core-flat-{label}")
            rows = _build_core_json(db, core_id=core_id)
            label = _safe(rows[0]["barcode"]) if rows else "core"
            return _json_response(rows, f"core-{label}")
        if flat:
            data = _build_core_rows(db, core_id=core_id)
            label = _safe(data[0]["barcode"]) if data else "core"
            return _respond(data, _CORE_FIELDS, f"core-flat-{label}")
        data = _build_core_with_tubes_rows(db, core_id=core_id)
        label = _safe(data[0]["core_barcode"]) if data else "core"
        return _respond(data, _CORE_WITH_TUBES_FIELDS, f"core-{label}")


def _parse_ids(raw: str) -> list[int] | None:
    if not raw:
        return None
    try:
        return [int(x) for x in raw.split(",") if x.strip()]
    except ValueError:
        return None


def _build_box_rows(db: Any, box_id: int | None = None, ids: list[int] | None = None) -> list[dict[str, Any]]:
    if box_id is not None:
        where = "WHERE b.id = ?"
        params: tuple = (box_id,)
    elif ids is not None:
        if not ids:
            return []
        where = f"WHERE b.id IN ({','.join('?' * len(ids))})"
        params = tuple(ids)
    else:
        where = ""
        params = ()
    return [
        dict(r)
        for r in db.execute(
            f"""
        SELECT b.barcode, b.name, l.name AS location, b.notes,
               COUNT(t.id) AS tube_count, b.created_at
        FROM boxes b
        LEFT JOIN locations l ON l.id = b.location_id
        LEFT JOIN tubes t ON t.box_id = b.id
        {where}
        GROUP BY b.id ORDER BY b.created_at DESC
    """,
            params,
        ).fetchall()
    ]


def _build_core_rows(db: Any, core_id: int | None = None, ids: list[int] | None = None) -> list[dict[str, Any]]:
    if core_id is not None:
        where = "WHERE c.id = ?"
        params: tuple = (core_id,)
    elif ids is not None:
        if not ids:
            return []
        where = f"WHERE c.id IN ({','.join('?' * len(ids))})"
        params = tuple(ids)
    else:
        where = ""
        params = ()
    return [
        dict(r)
        for r in db.execute(
            f"""
        SELECT c.barcode, c.name, l.name AS location, c.site_name,
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
    ]


def _build_box_with_tubes_rows(db: Any, box_id: int | None = None, ids: list[int] | None = None) -> list[dict[str, Any]]:
    if box_id is not None:
        where = "WHERE b.id = ?"
        params: tuple = (box_id,)
    elif ids is not None:
        if not ids:
            return []
        where = f"WHERE b.id IN ({','.join('?' * len(ids))})"
        params = tuple(ids)
    else:
        where = ""
        params = ()
    boxes = [
        dict(r)
        for r in db.execute(
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
    ]

    if box_id is not None:
        tube_where = "WHERE box_id = ?"
        tube_params: tuple = (box_id,)
    elif ids is not None:
        tube_where = f"WHERE box_id IN ({','.join('?' * len(ids))})"
        tube_params = tuple(ids)
    else:
        tube_where = "WHERE box_id IS NOT NULL"
        tube_params = ()
    tube_rows = [
        dict(r)
        for r in db.execute(
            f"""
        SELECT box_id, barcode, sample_date, site_name, latitude, longitude,
               sample_type, description, volume_ml, weight_g, depth_cm,
               created_at, updated_at
        FROM tubes {tube_where}
        ORDER BY depth_cm ASC, created_at ASC
    """,
            tube_params,
        ).fetchall()
    ]

    tubes_by_box: dict[int, list] = defaultdict(list)
    for t in tube_rows:
        tubes_by_box[t["box_id"]].append(t)

    _null: dict[str, Any] = {f: None for f in _BOX_WITH_TUBES_FIELDS}
    result = []
    for box in boxes:
        row = dict(_null)
        row.update(
            row_type="box",
            box_barcode=box["barcode"],
            box_name=box["name"],
            box_location=box["location"],
            box_notes=box["notes"],
            box_tube_count=box["tube_count"],
            box_created_at=box["created_at"],
        )
        result.append(row)

        for t in tubes_by_box[box["id"]]:
            row = dict(_null)
            row.update(
                row_type="tube",
                box_barcode=box["barcode"],
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


def _build_core_with_tubes_rows(db: Any, core_id: int | None = None, ids: list[int] | None = None) -> list[dict[str, Any]]:
    if core_id is not None:
        where = "WHERE c.id = ?"
        params: tuple = (core_id,)
    elif ids is not None:
        if not ids:
            return []
        where = f"WHERE c.id IN ({','.join('?' * len(ids))})"
        params = tuple(ids)
    else:
        where = ""
        params = ()
    cores = [
        dict(r)
        for r in db.execute(
            f"""
        SELECT c.id, c.barcode, c.name, l.name AS location_name, c.site_name,
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
    ]

    if core_id is not None:
        tube_where = "WHERE t.core_id = ?"
        tube_params: tuple = (core_id,)
    elif ids is not None:
        tube_where = f"WHERE t.core_id IN ({','.join('?' * len(ids))})"
        tube_params = tuple(ids)
    else:
        tube_where = "WHERE t.core_id IS NOT NULL"
        tube_params = ()
    tube_rows = [
        dict(r)
        for r in db.execute(
            f"""
        SELECT t.core_id, t.box_id, b.barcode AS box_barcode, b.name AS box_name,
               t.barcode, t.sample_date, t.site_name, t.latitude, t.longitude,
               t.sample_type, t.description, t.volume_ml, t.weight_g, t.depth_cm,
               t.created_at, t.updated_at
        FROM tubes t
        LEFT JOIN boxes b ON b.id = t.box_id
        {tube_where}
        ORDER BY CASE WHEN t.box_id IS NULL THEN 1 ELSE 0 END,
                 t.box_id, t.depth_cm ASC, t.created_at ASC
    """,
            tube_params,
        ).fetchall()
    ]

    tubes_by_core: dict[int, list] = defaultdict(list)
    for t in tube_rows:
        tubes_by_core[t["core_id"]].append(t)

    _null: dict[str, Any] = {f: None for f in _CORE_WITH_TUBES_FIELDS}
    result = []
    for core in cores:
        row = dict(_null)
        row.update(
            row_type="core",
            core_barcode=core["barcode"],
            core_name=core["name"],
            core_location=core["location_name"],
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

        # Group core's tubes by box (None = unboxed, sorted last by query)
        by_box: dict = {}
        for t in tubes_by_core[core["id"]]:
            key = t["box_id"]
            if key not in by_box:
                by_box[key] = []
            by_box[key].append(t)

        for box_id, box_tubes in by_box.items():
            first = box_tubes[0]
            if box_id is not None:
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


def _build_box_json(db: Any, box_id: int | None = None, ids: list[int] | None = None) -> list[dict[str, Any]]:
    if box_id is not None:
        where = "WHERE b.id = ?"
        params: tuple = (box_id,)
    elif ids is not None:
        if not ids:
            return []
        where = f"WHERE b.id IN ({','.join('?' * len(ids))})"
        params = tuple(ids)
    else:
        where = ""
        params = ()
    boxes = [
        dict(r)
        for r in db.execute(
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
    ]
    if not boxes:
        return []
    box_ids = [b["id"] for b in boxes]
    tube_rows = [
        dict(r)
        for r in db.execute(
            f"""
        SELECT box_id, barcode, sample_date, site_name, latitude, longitude,
               sample_type, description, volume_ml, weight_g, depth_cm,
               created_at, updated_at
        FROM tubes WHERE box_id IN ({','.join('?' * len(box_ids))})
        ORDER BY depth_cm ASC, created_at ASC
    """,
            tuple(box_ids),
        ).fetchall()
    ]
    tubes_by_box: dict[int, list] = defaultdict(list)
    for t in tube_rows:
        tubes_by_box[t["box_id"]].append({k: v for k, v in t.items() if k != "box_id"})
    return [
        {
            "barcode": b["barcode"],
            "name": b["name"],
            "location": b["location"],
            "notes": b["notes"],
            "tube_count": b["tube_count"],
            "created_at": b["created_at"],
            "tubes": tubes_by_box[b["id"]],
        }
        for b in boxes
    ]


def _build_core_json(db: Any, core_id: int | None = None, ids: list[int] | None = None) -> list[dict[str, Any]]:
    if core_id is not None:
        where = "WHERE c.id = ?"
        params: tuple = (core_id,)
    elif ids is not None:
        if not ids:
            return []
        where = f"WHERE c.id IN ({','.join('?' * len(ids))})"
        params = tuple(ids)
    else:
        where = ""
        params = ()
    cores = [
        dict(r)
        for r in db.execute(
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
    ]
    if not cores:
        return []
    core_ids = [c["id"] for c in cores]
    tube_rows = [
        dict(r)
        for r in db.execute(
            f"""
        SELECT t.core_id, t.box_id, b.barcode AS box_barcode, b.name AS box_name,
               t.barcode, t.sample_date, t.site_name, t.latitude, t.longitude,
               t.sample_type, t.description, t.volume_ml, t.weight_g, t.depth_cm,
               t.created_at, t.updated_at
        FROM tubes t
        LEFT JOIN boxes b ON b.id = t.box_id
        WHERE t.core_id IN ({','.join('?' * len(core_ids))})
        ORDER BY CASE WHEN t.box_id IS NULL THEN 1 ELSE 0 END,
                 t.box_id, t.depth_cm ASC, t.created_at ASC
    """,
            tuple(core_ids),
        ).fetchall()
    ]
    tubes_by_core: dict[int, list] = defaultdict(list)
    for t in tube_rows:
        tubes_by_core[t["core_id"]].append(t)

    result = []
    for core in cores:
        by_box: dict[int | None, dict] = {}
        for t in tubes_by_core[core["id"]]:
            key = t["box_id"]
            if key not in by_box:
                by_box[key] = {"barcode": t["box_barcode"], "name": t["box_name"], "tubes": []}
            by_box[key]["tubes"].append({
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
            })
        result.append({
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
        })
    return result


def _safe(value: str) -> str:
    """Sanitise a value for use in a filename."""
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in str(value))


def _respond(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    fmt = request.args.get("format", "csv")
    if fmt == "tsv":
        return _tsv_response(data, fields, basename)
    if fmt == "geojson":
        return _geojson_response(data, fields, basename)
    return _csv_response(data, fields, basename)


def _csv_response(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(data)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{basename}-{ts}.csv"
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _tsv_response(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fields,
        extrasaction="ignore",
        delimiter="\t",
        lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(data)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{basename}-{ts}.tsv"
    return Response(
        buf.getvalue(),
        mimetype="text/tab-separated-values",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _json_response(
    data: list[dict[str, Any]],
    basename: str,
) -> Response:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{basename}-{ts}.json"
    return Response(
        json.dumps(data, indent=2, default=str),
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _geojson_response(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    field_set = set(fields)
    coord_fields = {"latitude", "longitude"}
    prop_fields = [f for f in fields if f not in coord_fields]
    features = []
    for row in data:
        lat = row.get("latitude")
        lon = row.get("longitude")
        if lat is None or lon is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {f: row.get(f) for f in prop_fields if f in field_set},
        })
    collection = {"type": "FeatureCollection", "features": features}
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{basename}-{ts}.geojson"
    return Response(
        json.dumps(collection, indent=2, default=str),
        mimetype="application/geo+json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
