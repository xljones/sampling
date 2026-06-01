from typing import Any

from flask import Response, request
from flask_login import login_required

from dirtnap.db import get_db
from dirtnap.repositories.box_repository import BoxRepository
from dirtnap.repositories.tube_repository import TubeRepository

from ._blueprint import bp
from ._responses import _safe, json_response, parse_ids, respond, xlsx_response


def _boxes_xlsx(box_rows: list, db) -> Response:
    box_ids = [r["id"] for r in box_rows]
    tube_repo = TubeRepository(db)
    return xlsx_response(
        [
            {"name": "Boxes", "fields": BoxRepository.FLAT_FIELDS, "rows": box_rows},
            {
                "name": "Tubes",
                "fields": TubeRepository.EXPORT_FIELDS,
                "rows": tube_repo.export_for_boxes(box_ids),
            },
        ],
        "boxes",
    )


@bp.get("/api/export/boxes")
@login_required
def export_boxes() -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    ids = parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        repo = BoxRepository(db)
        if fmt == "xlsx":
            return _boxes_xlsx(repo.export_flat(ids=ids), db)
        if fmt == "json":
            if flat:
                rows: list[dict[str, Any]] = [
                    {f: r.get(f) for f in BoxRepository.FLAT_FIELDS}
                    for r in repo.export_flat(ids=ids)
                ]
            else:
                rows = repo.build_json(ids=ids)
            return json_response(rows, "boxes-flat" if flat else "boxes")
        if flat:
            return respond(repo.export_flat(ids=ids), BoxRepository.FLAT_FIELDS, "boxes-flat")
        return respond(
            repo.build_with_tubes_rows(ids=ids), BoxRepository.WITH_TUBES_FIELDS, "boxes"
        )


@bp.get("/api/export/boxes/<int:box_id>")
@login_required
def export_box(box_id: int) -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    with get_db() as db:
        repo = BoxRepository(db)
        if fmt == "xlsx":
            return _boxes_xlsx(repo.export_flat(box_id=box_id), db)
        if fmt == "json":
            if flat:
                data = repo.export_flat(box_id=box_id)
                label = _safe(data[0]["barcode"]) if data else "box"
                return json_response(
                    [{f: r.get(f) for f in BoxRepository.FLAT_FIELDS} for r in data],
                    f"box-flat-{label}",
                )
            rows = repo.build_json(box_id=box_id)
            label = _safe(rows[0]["barcode"]) if rows else "box"
            return json_response(rows, f"box-{label}")
        if flat:
            data = repo.export_flat(box_id=box_id)
            label = _safe(data[0]["barcode"]) if data else "box"
            return respond(data, BoxRepository.FLAT_FIELDS, f"box-flat-{label}")
        data = repo.build_with_tubes_rows(box_id=box_id)
        label = _safe(data[0]["box_barcode"]) if data else "box"
        return respond(data, BoxRepository.WITH_TUBES_FIELDS, f"box-{label}")
