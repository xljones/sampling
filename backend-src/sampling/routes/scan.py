from flask import Blueprint, Response, jsonify, request
from flask.typing import ResponseReturnValue
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.box_repository import BoxRepository
from sampling.repositories.core_repository import CoreRepository
from sampling.repositories.tube_repository import TubeRepository

bp = Blueprint("scan", __name__)


@bp.get("/api/scan/<barcode>")
@login_required
def scan(barcode: str) -> ResponseReturnValue:
    with get_db() as db:
        box = BoxRepository(db).get_by_barcode(barcode)
        if box:
            return jsonify(type="box", data=box)
        tube = TubeRepository(db).get_by_barcode(barcode)
        if tube:
            return jsonify(type="tube", data=tube)
        core = CoreRepository(db).get_by_barcode(barcode)
        if core:
            return jsonify(type="core", data=core)
    return jsonify(error="Barcode not found"), 404


@bp.get("/api/search")
@login_required
def search() -> Response:
    q = request.args.get("q", "")
    with get_db() as db:
        results = (
            BoxRepository(db).search(q)
            + TubeRepository(db).search(q)
            + CoreRepository(db).search(q)
        )
    return jsonify(results)
