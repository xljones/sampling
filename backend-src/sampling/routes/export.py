import csv
import io
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


@bp.get("/api/export/tubes")
@login_required
def export_tubes() -> Response:
    with get_db() as db:
        data = TubeRepository(db).export_all()
    return _respond(data, _TUBE_FIELDS, "tubes")


@bp.get("/api/export/boxes")
@login_required
def export_boxes() -> Response:
    with get_db() as db:
        data = _build_box_with_tubes_rows(db)
    return _respond(data, _BOX_WITH_TUBES_FIELDS, "boxes")


@bp.get("/api/export/boxes/<int:box_id>")
@login_required
def export_box(box_id: int) -> Response:
    with get_db() as db:
        data = _build_box_with_tubes_rows(db, box_id=box_id)
    label = _safe(data[0]["box_barcode"]) if data else "box"
    return _respond(data, _BOX_WITH_TUBES_FIELDS, f"box-{label}")


@bp.get("/api/export/cores")
@login_required
def export_cores() -> Response:
    with get_db() as db:
        data = _build_core_with_tubes_rows(db)
    return _respond(data, _CORE_WITH_TUBES_FIELDS, "cores")


@bp.get("/api/export/cores/<int:core_id>")
@login_required
def export_core(core_id: int) -> Response:
    with get_db() as db:
        data = _build_core_with_tubes_rows(db, core_id=core_id)
    label = _safe(data[0]["core_barcode"]) if data else "core"
    return _respond(data, _CORE_WITH_TUBES_FIELDS, f"core-{label}")


def _build_box_with_tubes_rows(db: Any, box_id: int | None = None) -> list[dict[str, Any]]:
    where = "WHERE b.id = ?" if box_id is not None else ""
    params: tuple = (box_id,) if box_id is not None else ()
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

    tube_where = "WHERE box_id = ?" if box_id is not None else "WHERE box_id IS NOT NULL"
    tube_params: tuple = (box_id,) if box_id is not None else ()
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

    _null = {f: None for f in _BOX_WITH_TUBES_FIELDS}
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


def _build_core_with_tubes_rows(db: Any, core_id: int | None = None) -> list[dict[str, Any]]:
    where = "WHERE c.id = ?" if core_id is not None else ""
    params: tuple = (core_id,) if core_id is not None else ()
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

    tube_where = "WHERE t.core_id = ?" if core_id is not None else "WHERE t.core_id IS NOT NULL"
    tube_params: tuple = (core_id,) if core_id is not None else ()
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

    _null = {f: None for f in _CORE_WITH_TUBES_FIELDS}
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
