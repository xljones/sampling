from flask import Response, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.tube_repository import TubeRepository

from ._blueprint import bp
from ._responses import json_response, parse_ids, respond, xlsx_response


@bp.get("/api/export/tubes")
@login_required
def export_tubes() -> Response:
    fmt = request.args.get("format", "csv")
    ids = parse_ids(request.args.get("ids", ""))
    with get_db() as db:
        data = TubeRepository(db).export_all(ids=ids)
    if fmt == "xlsx":
        return xlsx_response(
            [{"name": "Tubes", "fields": TubeRepository.EXPORT_FIELDS, "rows": data}],
            "tubes",
        )
    if fmt == "json":
        return json_response(
            [{f: r.get(f) for f in TubeRepository.EXPORT_FIELDS} for r in data], "tubes"
        )
    return respond(data, TubeRepository.EXPORT_FIELDS, "tubes")
