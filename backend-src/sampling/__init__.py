import os
import tomllib
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager

_DIST_DIR = str(Path(__file__).parent.parent.parent / "dist")
_PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"

login_manager = LoginManager()


def create_app():
    from sampling.db import get_db, run_migrations
    from sampling.domain.user import User
    from sampling.repositories.user_repository import UserRepository
    from sampling.routes import auth, boxes, export, scan, tubes

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
            return User(id=row["id"], username=row["username"], created_at=row.get("created_at"))
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify(error="Authentication required"), 401

    for bp in (auth.bp, boxes.bp, tubes.bp, scan.bp, export.bp):
        app.register_blueprint(bp)

    @app.get("/api/version")
    def version():
        try:
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
