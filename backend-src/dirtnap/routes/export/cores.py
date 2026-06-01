from flask import Response, request
from flask_login import login_required

from dirtnap.db import get_db
from dirtnap.repositories.box_repository import BoxRepository
from dirtnap.repositories.core_repository import CoreRepository
from dirtnap.repositories.tube_repository import TubeRepository

from ._blueprint import bp
from ._responses import _safe, json_response, parse_ids, respond, xlsx_response


def _cores_xlsx(core_rows: list, db) -> Response:
    core_ids = [r["id"] for r in core_rows]
    box_repo = BoxRepository(db)
    tube_repo = TubeRepository(db)
    return xlsx_response(
        [
            {"name": "Cores", "fields": CoreRepository.FLAT_FIELDS, "rows": core_rows},
            {
                "name": "Boxes",
                "fields": BoxRepository.FLAT_FIELDS,
                "rows": box_repo.export_flat_for_cores(core_ids),
            },
            {
                "name": "Tubes",
                "fields": TubeRepository.EXPORT_FIELDS,
                "rows": tube_repo.export_for_cores(core_ids),
            },
        ],
        "cores",
    )


@bp.get("/api/export/cores")
@login_required
def export_cores() -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    ids = parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        repo = CoreRepository(db)
        if fmt == "xlsx":
            return _cores_xlsx(repo.export_flat(ids=ids), db)
        if fmt == "json":
            if flat:
                rows = [
                    {f: r.get(f) for f in CoreRepository.FLAT_FIELDS}
                    for r in repo.export_flat(ids=ids)
                ]
            else:
                rows = repo.build_json(ids=ids)
            return json_response(rows, "cores-flat" if flat else "cores")
        if flat:
            return respond(repo.export_flat(ids=ids), CoreRepository.FLAT_FIELDS, "cores-flat")
        return respond(
            repo.build_with_tubes_rows(ids=ids), CoreRepository.WITH_TUBES_FIELDS, "cores"
        )


@bp.get("/api/export/cores/<int:core_id>")
@login_required
def export_core(core_id: int) -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    with get_db() as db:
        repo = CoreRepository(db)
        if fmt == "xlsx":
            return _cores_xlsx(repo.export_flat(core_id=core_id), db)
        if fmt == "json":
            if flat:
                data = repo.export_flat(core_id=core_id)
                label = _safe(data[0]["barcode"]) if data else "core"
                return json_response(
                    [{f: r.get(f) for f in CoreRepository.FLAT_FIELDS} for r in data],
                    f"core-flat-{label}",
                )
            rows = repo.build_json(core_id=core_id)
            label = _safe(rows[0]["barcode"]) if rows else "core"
            return json_response(rows, f"core-{label}")
        if flat:
            data = repo.export_flat(core_id=core_id)
            label = _safe(data[0]["barcode"]) if data else "core"
            return respond(data, CoreRepository.FLAT_FIELDS, f"core-flat-{label}")
        data = repo.build_with_tubes_rows(core_id=core_id)
        label = _safe(data[0]["core_barcode"]) if data else "core"
        return respond(data, CoreRepository.WITH_TUBES_FIELDS, f"core-{label}")
