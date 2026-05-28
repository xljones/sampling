from flask import Blueprint, request, jsonify, session
from sampling.db import get_db
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
        user = UserRepository(db).verify_password(username, password)
    if not user:
        return jsonify(error="Invalid username or password"), 401
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify(user)


@bp.post("/api/auth/logout")
def logout():
    session.clear()
    return "", 204


@bp.get("/api/auth/me")
def me():
    if "user_id" not in session:
        return jsonify(error="Not authenticated"), 401
    return jsonify(id=session["user_id"], username=session["username"])
