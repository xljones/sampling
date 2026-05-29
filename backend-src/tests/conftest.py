import os
import tempfile
from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    os.environ["DB_PATH"] = db_path

    # Import after setting DB_PATH so the app picks up the temp database.
    from sampling import create_app

    application = create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False

    yield application

    os.unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def auth_client(client: FlaskClient) -> FlaskClient:
    from sampling.db import get_db
    from sampling.repositories.user_repository import UserRepository

    with get_db() as db:
        UserRepository(db).create("testuser", "testpass")

    client.post("/api/auth/login", json={"username": "testuser", "password": "testpass"})
    return client
