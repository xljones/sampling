def test_list_boxes_requires_auth(client):
    r = client.get("/api/boxes")
    assert r.status_code == 401


def test_create_box(auth_client):
    r = auth_client.post("/api/boxes", json={"barcode": "BOX001", "name": "Shelf A"})
    assert r.status_code == 201
    assert r.json["barcode"] == "BOX001"
    assert r.json["name"] == "Shelf A"


def test_create_box_missing_barcode(auth_client):
    r = auth_client.post("/api/boxes", json={"name": "No barcode"})
    assert r.status_code == 400


def test_create_box_duplicate_barcode(auth_client):
    auth_client.post("/api/boxes", json={"barcode": "BOX001"})
    r = auth_client.post("/api/boxes", json={"barcode": "BOX001"})
    assert r.status_code == 409


def test_list_boxes(auth_client):
    auth_client.post("/api/boxes", json={"barcode": "BOX001"})
    auth_client.post("/api/boxes", json={"barcode": "BOX002"})
    r = auth_client.get("/api/boxes")
    assert r.status_code == 200
    assert len(r.json) == 2


def test_get_box_not_found(auth_client):
    r = auth_client.get("/api/boxes/999")
    assert r.status_code == 404


def test_update_box(auth_client):
    r = auth_client.post("/api/boxes", json={"barcode": "BOX001", "name": "Old"})
    box_id = r.json["id"]
    r = auth_client.put(f"/api/boxes/{box_id}", json={"barcode": "BOX001", "name": "New"})
    assert r.status_code == 200
    assert r.json["name"] == "New"


def test_delete_box(auth_client):
    r = auth_client.post("/api/boxes", json={"barcode": "BOX001"})
    box_id = r.json["id"]
    r = auth_client.delete(f"/api/boxes/{box_id}")
    assert r.status_code == 204
    r = auth_client.get(f"/api/boxes/{box_id}")
    assert r.status_code == 404
