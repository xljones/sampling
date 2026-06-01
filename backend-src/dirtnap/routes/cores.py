import sqlite3
from typing import Any

from flask import Blueprint, Response, jsonify, request
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required

from dirtnap.db import get_db
from dirtnap.repositories.core_repository import CoreRepository

bp = Blueprint("cores", __name__)


def _core_fields(d: dict[str, Any]) -> dict[str, Any]:
    return dict(
        name=d.get("name") or None,
        location_id=d.get("location_id") or None,
        latitude=d.get("latitude"),
        longitude=d.get("longitude"),
        site_name=d.get("site_name") or None,
        collection_date=d.get("collection_date") or None,
        depth_cm=d.get("depth_cm"),
        collector=d.get("collector") or None,
        sample_type=d.get("sample_type") or None,
        owner=d.get("owner") or None,
        notes=d.get("notes") or None,
    )


@bp.get("/api/cores")
@login_required
def list_cores() -> Response:
    with get_db() as db:
        return jsonify(CoreRepository(db).list_all())


@bp.post("/api/cores")
@login_required
def create_core() -> ResponseReturnValue:
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            core = CoreRepository(db).create(
                d["barcode"], changed_by=current_user.id, **_core_fields(d)
            )
            return jsonify(core), 201
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.get("/api/cores/<int:core_id>")
@login_required
def get_core(core_id: int) -> ResponseReturnValue:
    with get_db() as db:
        core = CoreRepository(db).get_with_tubes(core_id)
    if not core:
        return jsonify(error="Not found"), 404
    return jsonify(core)


@bp.put("/api/cores/<int:core_id>")
@login_required
def update_core(core_id: int) -> ResponseReturnValue:
    d = request.json or {}
    if not d.get("barcode"):
        return jsonify(error="barcode is required"), 400
    try:
        with get_db() as db:
            repo = CoreRepository(db)
            if not repo.get_by_id(core_id):
                return jsonify(error="Not found"), 404
            return jsonify(
                repo.update(core_id, d["barcode"], changed_by=current_user.id, **_core_fields(d))
            )
    except sqlite3.IntegrityError:
        return jsonify(error="Barcode already exists"), 409


@bp.delete("/api/cores/<int:core_id>")
@login_required
def delete_core(core_id: int) -> ResponseReturnValue:
    with get_db() as db:
        if not CoreRepository(db).delete(core_id):
            return jsonify(error="Not found"), 404
    return "", 204


@bp.get("/api/cores/<int:core_id>/history")
@login_required
def core_history(core_id: int) -> Response:
    with get_db() as db:
        return jsonify(CoreRepository(db).get_history(core_id))


@bp.post("/api/cores/<int:core_id>/revert/<int:version_id>")
@login_required
def revert_core(core_id: int, version_id: int) -> ResponseReturnValue:
    with get_db() as db:
        core = CoreRepository(db).revert(core_id, version_id, changed_by=current_user.id)
    if not core:
        return jsonify(error="Version not found"), 404
    return jsonify(core)
