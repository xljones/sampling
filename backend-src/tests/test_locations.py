from flask.testing import FlaskClient


def test_list_locations_requires_auth(client: FlaskClient) -> None:
    assert client.get("/api/locations").status_code == 401


def test_create_location(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/locations", json={"name": "Freezer 1"})
    assert r.status_code == 201
    assert r.json["name"] == "Freezer 1"


def test_create_location_missing_name(auth_client: FlaskClient) -> None:
    assert auth_client.post("/api/locations", json={}).status_code == 400
    assert auth_client.post("/api/locations", json={"name": "  "}).status_code == 400


def test_create_location_duplicate_name(auth_client: FlaskClient) -> None:
    auth_client.post("/api/locations", json={"name": "Freezer 1"})
    assert auth_client.post("/api/locations", json={"name": "Freezer 1"}).status_code == 409


def test_list_locations(auth_client: FlaskClient) -> None:
    auth_client.post("/api/locations", json={"name": "Freezer 1"})
    auth_client.post("/api/locations", json={"name": "Shelf A"})
    r = auth_client.get("/api/locations")
    assert r.status_code == 200
    assert len(r.json) == 2


def test_get_location(auth_client: FlaskClient) -> None:
    loc = auth_client.post("/api/locations", json={"name": "Lab B"}).json
    r = auth_client.get(f"/api/locations/{loc['id']}")
    assert r.status_code == 200
    assert r.json["name"] == "Lab B"
    assert isinstance(r.json["boxes"], list)


def test_get_location_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.get("/api/locations/9999").status_code == 404


def test_update_location(auth_client: FlaskClient) -> None:
    loc = auth_client.post("/api/locations", json={"name": "Old Name"}).json
    r = auth_client.put(f"/api/locations/{loc['id']}", json={"name": "New Name"})
    assert r.status_code == 200
    assert r.json["name"] == "New Name"


def test_update_location_missing_name(auth_client: FlaskClient) -> None:
    loc = auth_client.post("/api/locations", json={"name": "Lab"}).json
    assert auth_client.put(f"/api/locations/{loc['id']}", json={"name": ""}).status_code == 400


def test_update_location_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.put("/api/locations/9999", json={"name": "X"}).status_code == 404


def test_update_location_duplicate_name(auth_client: FlaskClient) -> None:
    auth_client.post("/api/locations", json={"name": "Lab A"})
    loc2 = auth_client.post("/api/locations", json={"name": "Lab B"}).json
    assert auth_client.put(f"/api/locations/{loc2['id']}", json={"name": "Lab A"}).status_code == 409


def test_delete_location(auth_client: FlaskClient) -> None:
    loc = auth_client.post("/api/locations", json={"name": "Temp Lab"}).json
    assert auth_client.delete(f"/api/locations/{loc['id']}").status_code == 204
    assert auth_client.get(f"/api/locations/{loc['id']}").status_code == 404


def test_delete_location_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.delete("/api/locations/9999").status_code == 404


def test_delete_location_with_boxes_fails(auth_client: FlaskClient) -> None:
    loc = auth_client.post("/api/locations", json={"name": "In Use"}).json
    auth_client.post("/api/boxes", json={"barcode": "BOX001", "location_id": loc["id"]})
    r = auth_client.delete(f"/api/locations/{loc['id']}")
    assert r.status_code == 409
    assert "box" in r.json["error"].lower()
