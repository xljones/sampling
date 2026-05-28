import sqlite3

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

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
@login_required
def list_tubes():
    with get_db() as db:
        return jsonify(TubeRepository(db).list_all())


@bp.post("/api/tubes")
@login_required
def create_tube():
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            tube = TubeRepository(db).create(
                d["barcode"], changed_by=current_user.id, **_tube_fields(d)
            )
            return jsonify(tube), 201
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.get("/api/tubes/<int:tube_id>")
@login_required
def get_tube(tube_id):
    with get_db() as db:
        tube = TubeRepository(db).get_by_id(tube_id)
    if not tube:
        return jsonify(error="Not found"), 404
    return jsonify(tube)


@bp.put("/api/tubes/<int:tube_id>")
@login_required
def update_tube(tube_id):
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            repo = TubeRepository(db)
            if not repo.get_by_id(tube_id):
                return jsonify(error="Not found"), 404
            return jsonify(
                repo.update(tube_id, d["barcode"], changed_by=current_user.id, **_tube_fields(d))
            )
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.post("/api/tubes/bulk-assign")
@login_required
def bulk_assign_tubes():
    d = request.json or {}
    tube_ids = d.get("tube_ids", [])
    box_id = d.get("box_id")
    if not tube_ids or box_id is None:
        return jsonify(error="tube_ids and box_id are required"), 400
    with get_db() as db:
        count = TubeRepository(db).bulk_assign(tube_ids, box_id, changed_by=current_user.id)
    return jsonify(assigned=count)


@bp.delete("/api/tubes/<int:tube_id>")
@login_required
def delete_tube(tube_id):
    with get_db() as db:
        if not TubeRepository(db).delete(tube_id):
            return jsonify(error="Not found"), 404
    return "", 204


@bp.get("/api/tubes/<int:tube_id>/history")
@login_required
def tube_history(tube_id):
    with get_db() as db:
        return jsonify(TubeRepository(db).get_history(tube_id))


@bp.post("/api/tubes/<int:tube_id>/revert/<int:version_id>")
@login_required
def revert_tube(tube_id, version_id):
    with get_db() as db:
        tube = TubeRepository(db).revert(tube_id, version_id, changed_by=current_user.id)
    if not tube:
        return jsonify(error="Version not found"), 404
    return jsonify(tube)
