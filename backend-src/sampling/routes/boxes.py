import sqlite3

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from sampling.db import get_db
from sampling.repositories.box_repository import BoxRepository

bp = Blueprint("boxes", __name__)


@bp.get("/api/boxes")
@login_required
def list_boxes():
    with get_db() as db:
        return jsonify(BoxRepository(db).list_all())


@bp.post("/api/boxes")
@login_required
def create_box():
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            box = BoxRepository(db).create(
                d["barcode"], d.get("name"), d.get("location"), d.get("notes"),
                changed_by=current_user.id,
            )
            return jsonify(box), 201
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.get("/api/boxes/<int:box_id>")
@login_required
def get_box(box_id):
    with get_db() as db:
        box = BoxRepository(db).get_with_tubes(box_id)
    if not box:
        return jsonify(error="Not found"), 404
    return jsonify(box)


@bp.put("/api/boxes/<int:box_id>")
@login_required
def update_box(box_id):
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            repo = BoxRepository(db)
            if not repo.get_by_id(box_id):
                return jsonify(error="Not found"), 404
            return jsonify(repo.update(
                box_id, d["barcode"], d.get("name"), d.get("location"), d.get("notes"),
                changed_by=current_user.id,
            ))
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.post("/api/boxes/<int:box_id>/empty")
@login_required
def empty_box(box_id):
    with get_db() as db:
        repo = BoxRepository(db)
        if not repo.get_by_id(box_id):
            return jsonify(error="Not found"), 404
        repo.empty(box_id)
    return "", 204


@bp.delete("/api/boxes/<int:box_id>")
@login_required
def delete_box(box_id):
    with get_db() as db:
        if not BoxRepository(db).delete(box_id):
            return jsonify(error="Not found"), 404
    return "", 204


@bp.get("/api/boxes/<int:box_id>/history")
@login_required
def box_history(box_id):
    with get_db() as db:
        return jsonify(BoxRepository(db).get_history(box_id))


@bp.post("/api/boxes/<int:box_id>/revert/<int:version_id>")
@login_required
def revert_box(box_id, version_id):
    with get_db() as db:
        box = BoxRepository(db).revert(box_id, version_id, changed_by=current_user.id)
    if not box:
        return jsonify(error="Version not found"), 404
    return jsonify(box)
