from flask.testing import FlaskClient

from sampling.db import get_db
from sampling.repositories.user_repository import UserRepository


def test_list_users_requires_auth(client: FlaskClient) -> None:
    assert client.get("/api/users").status_code == 401


def test_list_users(auth_client: FlaskClient) -> None:
    r = auth_client.get("/api/users")
    assert r.status_code == 200
    assert isinstance(r.json, list)
    assert any(u["username"] == "testuser" for u in r.json)


def test_create_user(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/users", json={"username": "newuser", "password": "securepass"})
    assert r.status_code == 201
    assert r.json["username"] == "newuser"
    assert r.json["is_readonly"] is True


def test_create_user_with_ttl(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/users", json={
        "username": "tempuser", "password": "securepass", "ttl_days": 7
    })
    assert r.status_code == 201
    assert r.json["expires_at"] is not None


def test_create_user_missing_fields(auth_client: FlaskClient) -> None:
    assert auth_client.post("/api/users", json={"username": "x"}).status_code == 400
    assert auth_client.post("/api/users", json={"password": "x"}).status_code == 400


def test_create_user_invalid_ttl(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/users", json={
        "username": "u", "password": "pass", "ttl_days": -1
    })
    assert r.status_code == 400


def test_create_user_non_integer_ttl(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/users", json={
        "username": "u", "password": "pass", "ttl_days": "abc"
    })
    assert r.status_code == 400


def test_create_user_duplicate_username(auth_client: FlaskClient) -> None:
    auth_client.post("/api/users", json={"username": "dup", "password": "pass"})
    assert auth_client.post("/api/users", json={"username": "dup", "password": "pass"}).status_code == 409


def test_delete_user(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/users", json={"username": "readonly1", "password": "pass"})
    user_id = r.json["id"]
    assert auth_client.delete(f"/api/users/{user_id}").status_code == 204


def test_delete_user_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.delete("/api/users/9999").status_code == 404


def test_delete_own_account_forbidden(auth_client: FlaskClient) -> None:
    me = auth_client.get("/api/auth/me").json
    assert auth_client.delete(f"/api/users/{me['id']}").status_code == 400


def test_delete_non_readonly_account_forbidden(auth_client: FlaskClient) -> None:
    with get_db() as db:
        other = UserRepository(db).create("admin2", "pass", is_readonly=False)
    r = auth_client.delete(f"/api/users/{other['id']}")
    assert r.status_code == 403


def test_user_repository_rename() -> None:
    import os, tempfile
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    os.environ["DB_PATH"] = db_path
    try:
        from sampling.db import run_migrations, get_db
        run_migrations()
        with get_db() as db:
            user = UserRepository(db).create("original", "pass")
            UserRepository(db).rename(user["id"], "renamed")
            updated = UserRepository(db).get_by_id(user["id"])
        assert updated["username"] == "renamed"
    finally:
        os.unlink(db_path)
        os.environ.pop("DB_PATH", None)
