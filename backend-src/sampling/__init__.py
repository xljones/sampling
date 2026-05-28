import os
from pathlib import Path
from flask import Flask, send_from_directory, request, jsonify, session
from flask_cors import CORS

_DIST_DIR = str(Path(__file__).parent.parent.parent / "dist")


def create_app():
    from sampling.db import run_migrations
    from sampling.routes import boxes, tubes, scan, export, auth

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

    for bp in (auth.bp, boxes.bp, tubes.bp, scan.bp, export.bp):
        app.register_blueprint(bp)

    @app.before_request
    def require_login():
        if request.path.startswith("/api/") and not request.path.startswith("/api/auth/"):
            if "user_id" not in session:
                return jsonify(error="Authentication required"), 401

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def serve_frontend(path):
        full = os.path.join(_DIST_DIR, path)
        if path and os.path.exists(full):
            return send_from_directory(_DIST_DIR, path)
        return send_from_directory(_DIST_DIR, "index.html")

    return app
