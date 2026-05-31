from flask.testing import FlaskClient


def test_list_cores_requires_auth(client: FlaskClient) -> None:
    assert client.get("/api/cores").status_code == 401


def test_create_core(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/cores", json={"barcode": "CORE001"})
    assert r.status_code == 201
    assert r.json["barcode"] == "CORE001"


def test_create_core_with_fields(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/cores", json={
        "barcode": "CORE001",
        "name": "North Sea Core",
        "site_name": "Block 49",
        "latitude": 51.5,
        "longitude": -0.1,
        "depth_cm": 300.0,
        "sample_type": "piston",
        "collector": "RV Explorer",
        "owner": "Lab A",
        "notes": "test notes",
    })
    assert r.status_code == 201
    assert r.json["name"] == "North Sea Core"
    assert r.json["depth_cm"] == 300.0


def test_create_core_missing_barcode(auth_client: FlaskClient) -> None:
    assert auth_client.post("/api/cores", json={"name": "No barcode"}).status_code == 400


def test_create_core_duplicate_barcode(auth_client: FlaskClient) -> None:
    auth_client.post("/api/cores", json={"barcode": "CORE001"})
    assert auth_client.post("/api/cores", json={"barcode": "CORE001"}).status_code == 409


def test_list_cores(auth_client: FlaskClient) -> None:
    auth_client.post("/api/cores", json={"barcode": "CORE001"})
    auth_client.post("/api/cores", json={"barcode": "CORE002"})
    r = auth_client.get("/api/cores")
    assert r.status_code == 200
    assert len(r.json) == 2


def test_get_core(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001", "name": "Deep Core"}).json
    r = auth_client.get(f"/api/cores/{core['id']}")
    assert r.status_code == 200
    assert r.json["barcode"] == "CORE001"
    assert isinstance(r.json["tubes"], list)


def test_get_core_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.get("/api/cores/9999").status_code == 404


def test_update_core(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001"}).json
    r = auth_client.put(f"/api/cores/{core['id']}", json={"barcode": "CORE001", "name": "Updated"})
    assert r.status_code == 200
    assert r.json["name"] == "Updated"


def test_update_core_missing_barcode(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001"}).json
    assert auth_client.put(f"/api/cores/{core['id']}", json={"name": "No barcode"}).status_code == 400


def test_update_core_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.put("/api/cores/9999", json={"barcode": "CORE001"}).status_code == 404


def test_update_core_duplicate_barcode(auth_client: FlaskClient) -> None:
    auth_client.post("/api/cores", json={"barcode": "CORE001"})
    core2 = auth_client.post("/api/cores", json={"barcode": "CORE002"}).json
    assert auth_client.put(f"/api/cores/{core2['id']}", json={"barcode": "CORE001"}).status_code == 409


def test_delete_core(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001"}).json
    assert auth_client.delete(f"/api/cores/{core['id']}").status_code == 204
    assert auth_client.get(f"/api/cores/{core['id']}").status_code == 404


def test_delete_core_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.delete("/api/cores/9999").status_code == 404


def test_core_history(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001"}).json
    r = auth_client.get(f"/api/cores/{core['id']}/history")
    assert r.status_code == 200
    assert isinstance(r.json, list)
    assert len(r.json) >= 1


def test_revert_core(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001", "name": "Original"}).json
    auth_client.put(f"/api/cores/{core['id']}", json={"barcode": "CORE001", "name": "Changed"})
    history = auth_client.get(f"/api/cores/{core['id']}/history").json
    first_version = history[-1]
    r = auth_client.post(f"/api/cores/{core['id']}/revert/{first_version['id']}")
    assert r.status_code == 200
    assert r.json["name"] == "Original"


def test_revert_core_not_found(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001"}).json
    assert auth_client.post(f"/api/cores/{core['id']}/revert/9999").status_code == 404


def test_scan_core(auth_client: FlaskClient) -> None:
    auth_client.post("/api/cores", json={"barcode": "CORE-SCAN"})
    r = auth_client.get("/api/scan/CORE-SCAN")
    assert r.status_code == 200
    assert r.json["type"] == "core"
    assert r.json["data"]["barcode"] == "CORE-SCAN"
