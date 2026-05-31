from flask import Response, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.core_repository import CoreRepository

from ._blueprint import bp
from ._responses import _safe, json_response, parse_ids, respond


@bp.get("/api/export/cores")
@login_required
def export_cores() -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    ids = parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        repo = CoreRepository(db)
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
