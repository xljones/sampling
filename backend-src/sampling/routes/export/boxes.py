from typing import Any

from flask import Response, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.box_repository import BoxRepository

from ._blueprint import bp
from ._fields import BOX_FIELDS, BOX_WITH_TUBES_FIELDS
from ._queries import build_box_json, build_box_with_tubes_rows, parse_ids
from ._responses import _safe, json_response, respond


@bp.get("/api/export/boxes")
@login_required
def export_boxes() -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    ids = parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        if fmt == "json":
            if flat:
                rows: list[dict[str, Any]] = [
                    {f: r.get(f) for f in BOX_FIELDS}
                    for r in BoxRepository(db).export_flat(ids=ids)
                ]
            else:
                rows = build_box_json(db, ids=ids)
            return json_response(rows, "boxes-flat" if flat else "boxes")
        if flat:
            return respond(BoxRepository(db).export_flat(ids=ids), BOX_FIELDS, "boxes-flat")
        return respond(build_box_with_tubes_rows(db, ids=ids), BOX_WITH_TUBES_FIELDS, "boxes")


@bp.get("/api/export/boxes/<int:box_id>")
@login_required
def export_box(box_id: int) -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    with get_db() as db:
        if fmt == "json":
            if flat:
                data = BoxRepository(db).export_flat(box_id=box_id)
                label = _safe(data[0]["barcode"]) if data else "box"
                return json_response(
                    [{f: r.get(f) for f in BOX_FIELDS} for r in data], f"box-flat-{label}"
                )
            rows = build_box_json(db, box_id=box_id)
            label = _safe(rows[0]["barcode"]) if rows else "box"
            return json_response(rows, f"box-{label}")
        if flat:
            data = BoxRepository(db).export_flat(box_id=box_id)
            label = _safe(data[0]["barcode"]) if data else "box"
            return respond(data, BOX_FIELDS, f"box-flat-{label}")
        data = build_box_with_tubes_rows(db, box_id=box_id)
        label = _safe(data[0]["box_barcode"]) if data else "box"
        return respond(data, BOX_WITH_TUBES_FIELDS, f"box-{label}")
