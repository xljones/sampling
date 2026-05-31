from flask import Response, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.tube_repository import TubeRepository

from ._blueprint import bp
from ._fields import TUBE_FIELDS
from ._responses import json_response, respond


@bp.get("/api/export/tubes")
@login_required
def export_tubes() -> Response:
    fmt = request.args.get("format", "csv")
    with get_db() as db:
        data = TubeRepository(db).export_all()
    if fmt == "json":
        return json_response([{f: r.get(f) for f in TUBE_FIELDS} for r in data], "tubes")
    return respond(data, TUBE_FIELDS, "tubes")
