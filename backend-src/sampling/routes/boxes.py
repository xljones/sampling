import sqlite3
from flask import Blueprint, request, jsonify
from flask_login import login_required
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
                d["barcode"], d.get("name"), d.get("location"), d.get("notes")
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
                box_id, d["barcode"], d.get("name"), d.get("location"), d.get("notes")
            ))
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.delete("/api/boxes/<int:box_id>")
@login_required
def delete_box(box_id):
    with get_db() as db:
        if not BoxRepository(db).delete(box_id):
            return jsonify(error="Not found"), 404
    return "", 204
