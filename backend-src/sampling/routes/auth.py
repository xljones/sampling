from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from sampling.db import get_db
from sampling.domain.user import User
from sampling.repositories.user_repository import UserRepository

bp = Blueprint("auth", __name__)


@bp.post("/api/auth/login")
def login():
    d = request.json or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""
    if not username or not password:
        return jsonify(error="Username and password required"), 400
    with get_db() as db:
        row = UserRepository(db).verify_password(username, password)
    if not row:
        return jsonify(error="Invalid username or password"), 401
    login_user(User(id=row["id"], username=row["username"]))
    return jsonify({"id": row["id"], "username": row["username"]})


@bp.post("/api/auth/logout")
def logout():
    logout_user()
    return "", 204


@bp.get("/api/auth/me")
@login_required
def me():
    return jsonify(id=current_user.id, username=current_user.username)
