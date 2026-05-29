from flask.testing import FlaskClient


def test_list_boxes_requires_auth(client: FlaskClient) -> None:
    r = client.get("/api/boxes")
    assert r.status_code == 401


def test_create_box(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/boxes", json={"barcode": "BOX001", "name": "Shelf A"})
    assert r.status_code == 201
    assert r.json["barcode"] == "BOX001"
    assert r.json["name"] == "Shelf A"


def test_create_box_missing_barcode(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/boxes", json={"name": "No barcode"})
    assert r.status_code == 400


def test_create_box_duplicate_barcode(auth_client: FlaskClient) -> None:
    auth_client.post("/api/boxes", json={"barcode": "BOX001"})
    r = auth_client.post("/api/boxes", json={"barcode": "BOX001"})
    assert r.status_code == 409


def test_list_boxes(auth_client: FlaskClient) -> None:
    auth_client.post("/api/boxes", json={"barcode": "BOX001"})
    auth_client.post("/api/boxes", json={"barcode": "BOX002"})
    r = auth_client.get("/api/boxes")
    assert r.status_code == 200
    assert len(r.json) == 2
