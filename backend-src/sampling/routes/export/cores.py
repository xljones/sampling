from flask import Response, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.core_repository import CoreRepository

from ._blueprint import bp
from ._fields import CORE_FIELDS, CORE_WITH_TUBES_FIELDS
from ._queries import build_core_json, build_core_with_tubes_rows, parse_ids
from ._responses import _safe, json_response, respond


@bp.get("/api/export/cores")
@login_required
def export_cores() -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    ids = parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        if fmt == "json":
            if flat:
                rows = [
                    {f: r.get(f) for f in CORE_FIELDS}
                    for r in CoreRepository(db).export_flat(ids=ids)
                ]
            else:
                rows = build_core_json(db, ids=ids)
            return json_response(rows, "cores-flat" if flat else "cores")
        if flat:
            return respond(CoreRepository(db).export_flat(ids=ids), CORE_FIELDS, "cores-flat")
        return respond(build_core_with_tubes_rows(db, ids=ids), CORE_WITH_TUBES_FIELDS, "cores")


@bp.get("/api/export/cores/<int:core_id>")
@login_required
def export_core(core_id: int) -> Response:
    fmt = request.args.get("format", "csv")
    flat = request.args.get("flat", "").lower() in ("1", "true", "yes")
    with get_db() as db:
        if fmt == "json":
            if flat:
                data = CoreRepository(db).export_flat(core_id=core_id)
                label = _safe(data[0]["barcode"]) if data else "core"
                return json_response(
                    [{f: r.get(f) for f in CORE_FIELDS} for r in data], f"core-flat-{label}"
                )
            rows = build_core_json(db, core_id=core_id)
            label = _safe(rows[0]["barcode"]) if rows else "core"
            return json_response(rows, f"core-{label}")
        if flat:
            data = CoreRepository(db).export_flat(core_id=core_id)
            label = _safe(data[0]["barcode"]) if data else "core"
            return respond(data, CORE_FIELDS, f"core-flat-{label}")
        data = build_core_with_tubes_rows(db, core_id=core_id)
        label = _safe(data[0]["core_barcode"]) if data else "core"
        return respond(data, CORE_WITH_TUBES_FIELDS, f"core-{label}")
