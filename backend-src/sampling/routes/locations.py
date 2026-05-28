import sqlite3

from flask import Blueprint, jsonify, request
from flask_login import login_required

from sampling.db import get_db
from sampling.repositories.location_repository import LocationRepository

bp = Blueprint("locations", __name__)


@bp.get("/api/locations")
@login_required
def list_locations():
    with get_db() as db:
        return jsonify(LocationRepository(db).list_all())


@bp.get("/api/locations/<int:loc_id>")
@login_required
def get_location(loc_id):
    with get_db() as db:
        loc = LocationRepository(db).get_with_boxes(loc_id)
    if not loc:
        return jsonify(error="Not found"), 404
    return jsonify(loc)


@bp.post("/api/locations")
@login_required
def create_location():
    d = request.json or {}
    if not d.get("name", "").strip():
        return jsonify(error="name is required"), 400
    try:
        with get_db() as db:
            loc = LocationRepository(db).create(d["name"].strip())
        return jsonify(loc), 201
    except sqlite3.IntegrityError:
        return jsonify(error="Location name already exists"), 409


@bp.put("/api/locations/<int:loc_id>")
@login_required
def update_location(loc_id):
    d = request.json or {}
    if not d.get("name", "").strip():
        return jsonify(error="name is required"), 400
    try:
        with get_db() as db:
            repo = LocationRepository(db)
            if not repo.get_by_id(loc_id):
                return jsonify(error="Not found"), 404
            return jsonify(repo.update(loc_id, d["name"].strip()))
    except sqlite3.IntegrityError:
        return jsonify(error="Location name already exists"), 409


@bp.delete("/api/locations/<int:loc_id>")
@login_required
def delete_location(loc_id):
    with get_db() as db:
        repo = LocationRepository(db)
        if not repo.get_by_id(loc_id):
            return jsonify(error="Not found"), 404
        ok, err = repo.delete(loc_id)
        if not ok:
            return jsonify(error=err), 409
    return "", 204
