import sqlite3
from flask import Blueprint, request, jsonify
from sampling.db import get_db
from sampling.repositories.tube_repository import TubeRepository

bp = Blueprint("tubes", __name__)


def _tube_fields(d):
    return dict(
        box_id=d.get("box_id") or None,
        collection_date=d.get("collection_date") or None,
        site_name=d.get("site_name") or None,
        latitude=d.get("latitude"),
        longitude=d.get("longitude"),
        sample_type=d.get("sample_type") or None,
        description=d.get("description") or None,
        volume_ml=d.get("volume_ml"),
        weight_g=d.get("weight_g"),
        depth_cm=d.get("depth_cm"),
    )


@bp.get("/api/tubes")
def list_tubes():
    with get_db() as db:
        return jsonify(TubeRepository(db).list_all())


@bp.post("/api/tubes")
def create_tube():
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            tube = TubeRepository(db).create(d["barcode"], **_tube_fields(d))
            return jsonify(tube), 201
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.get("/api/tubes/<int:tube_id>")
def get_tube(tube_id):
    with get_db() as db:
        tube = TubeRepository(db).get_by_id(tube_id)
    if not tube:
        return jsonify(error="Not found"), 404
    return jsonify(tube)


@bp.put("/api/tubes/<int:tube_id>")
def update_tube(tube_id):
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            repo = TubeRepository(db)
            if not repo.get_by_id(tube_id):
                return jsonify(error="Not found"), 404
            return jsonify(repo.update(tube_id, d["barcode"], **_tube_fields(d)))
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.delete("/api/tubes/<int:tube_id>")
def delete_tube(tube_id):
    with get_db() as db:
        if not TubeRepository(db).delete(tube_id):
            return jsonify(error="Not found"), 404
    return "", 204
