import os

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, current_user, logout_user

_DIST_DIR = str(Path(__file__).parent.parent.parent / "dist")


def _find_pyproject():
    p = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = p / "pyproject.toml"
        if candidate.exists():
            return candidate
        p = p.parent
    return None


_PYPROJECT = _find_pyproject()

login_manager = LoginManager()


def create_app():
    from sampling.db import get_db, run_migrations
    from sampling.domain.user import User
    from sampling.repositories.user_repository import UserRepository
    from sampling.routes import auth, boxes, export, locations, scan, tubes, users

    run_migrations()

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        if os.environ.get("FLASK_DEBUG", "1") == "0":
            raise RuntimeError("SECRET_KEY environment variable must be set in production")
        secret_key = "dev-secret-key-change-in-production"

    app = Flask(__name__, static_folder=_DIST_DIR)
    app.config["SECRET_KEY"] = secret_key
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    CORS(app, supports_credentials=True)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        with get_db() as db:
            row = UserRepository(db).get_by_id(int(user_id))
        if row:
            return User(
                id=row["id"],
                username=row["username"],
                created_at=row.get("created_at"),
                is_readonly=bool(row.get("is_readonly")),
                expires_at=row.get("expires_at"),
            )
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify(error="Authentication required"), 401

    @app.before_request
    def enforce_auth():
        if not current_user.is_authenticated:
            return
        if current_user.expires_at:
            try:
                if datetime.now(timezone.utc) >= datetime.fromisoformat(current_user.expires_at):
                    logout_user()
                    return jsonify(error="Account expired"), 401
            except ValueError:
                pass
        if (
            current_user.is_readonly
            and request.method not in ("GET", "HEAD", "OPTIONS")
            and request.path != "/api/auth/password"
        ):
            return jsonify(error="Read-only access"), 403

    for bp in (auth.bp, boxes.bp, tubes.bp, scan.bp, export.bp, locations.bp, users.bp):
        app.register_blueprint(bp)

    @app.get("/api/version")
    def version():
        try:
            if tomllib is None or _PYPROJECT is None:
                raise RuntimeError("no toml parser or pyproject.toml not found")
            with open(_PYPROJECT, "rb") as f:
                v = tomllib.load(f)["project"]["version"]
        except Exception:
            v = "unknown"
        return jsonify(version=v)

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def serve_frontend(path):
        full = os.path.join(_DIST_DIR, path)
        if path and os.path.exists(full):
            return send_from_directory(_DIST_DIR, path)
        return send_from_directory(_DIST_DIR, "index.html")

    return app
