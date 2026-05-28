from sampling.db import get_db
from sampling.repositories.user_repository import UserRepository


def test_login_success(client, app):
    with app.app_context():
        with get_db() as db:
            UserRepository(db).create("alice", "secret")

    r = client.post("/api/auth/login", json={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    assert r.json["username"] == "alice"


def test_login_wrong_password(client, app):
    with app.app_context():
        with get_db() as db:
            UserRepository(db).create("alice", "secret")

    r = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_login_missing_fields(client):
    r = client.post("/api/auth/login", json={"username": "alice"})
    assert r.status_code == 400


def test_me_unauthenticated(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_authenticated(auth_client):
    r = auth_client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json["username"] == "testuser"


def test_logout(auth_client):
    r = auth_client.post("/api/auth/logout")
    assert r.status_code == 204

    r = auth_client.get("/api/auth/me")
    assert r.status_code == 401
