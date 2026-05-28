from flask import Blueprint, jsonify, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.box_repository import BoxRepository
from sampling.repositories.tube_repository import TubeRepository

bp = Blueprint("scan", __name__)


@bp.get("/api/scan/<barcode>")
@login_required
def scan(barcode):
    with get_db() as db:
        box = BoxRepository(db).get_by_barcode(barcode)
        if box:
            return jsonify(type="box", data=box)
        tube = TubeRepository(db).get_by_barcode(barcode)
        if tube:
            return jsonify(type="tube", data=tube)
    return jsonify(error="Barcode not found"), 404


@bp.get("/api/search")
@login_required
def search():
    q = request.args.get("q", "")
    with get_db() as db:
        results = BoxRepository(db).search(q) + TubeRepository(db).search(q)
    return jsonify(results)
