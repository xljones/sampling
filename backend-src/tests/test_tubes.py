def test_list_tubes_requires_auth(client):
    r = client.get("/api/tubes")
    assert r.status_code == 401


def test_create_tube(auth_client):
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    assert r.status_code == 201
    assert r.json["barcode"] == "TUBE001"
    assert r.json["box_id"] is None


def test_create_tube_with_box(auth_client):
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]})
    assert r.status_code == 201
    assert r.json["box_id"] == box["id"]
    assert r.json["box_barcode"] == "BOX001"


def test_create_tube_missing_barcode(auth_client):
    r = auth_client.post("/api/tubes", json={"site_name": "Lake"})
    assert r.status_code == 400


def test_create_tube_duplicate_barcode(auth_client):
    auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    assert r.status_code == 409


def test_get_tube(auth_client):
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "site_name": "River A"})
    tube_id = r.json["id"]
    r = auth_client.get(f"/api/tubes/{tube_id}")
    assert r.status_code == 200
    assert r.json["site_name"] == "River A"


def test_get_tube_not_found(auth_client):
    r = auth_client.get("/api/tubes/999")
    assert r.status_code == 404


def test_update_tube(auth_client):
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "site_name": "Old Site"})
    tube_id = r.json["id"]
    r = auth_client.put(f"/api/tubes/{tube_id}", json={"barcode": "TUBE001", "site_name": "New Site"})
    assert r.status_code == 200
    assert r.json["site_name"] == "New Site"


def test_update_tube_not_found(auth_client):
    r = auth_client.put("/api/tubes/999", json={"barcode": "TUBE001"})
    assert r.status_code == 404


def test_update_tube_duplicate_barcode(auth_client):
    auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE002"})
    tube_id = r.json["id"]
    r = auth_client.put(f"/api/tubes/{tube_id}", json={"barcode": "TUBE001"})
    assert r.status_code == 409


def test_delete_tube(auth_client):
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    tube_id = r.json["id"]
    r = auth_client.delete(f"/api/tubes/{tube_id}")
    assert r.status_code == 204
    r = auth_client.get(f"/api/tubes/{tube_id}")
    assert r.status_code == 404


def test_delete_tube_not_found(auth_client):
    r = auth_client.delete("/api/tubes/999")
    assert r.status_code == 404


def test_assign_tube_to_box(auth_client):
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    tube = auth_client.post("/api/tubes", json={"barcode": "TUBE001"}).json
    r = auth_client.put(f"/api/tubes/{tube['id']}", json={"barcode": "TUBE001", "box_id": box["id"]})
    assert r.status_code == 200
    assert r.json["box_id"] == box["id"]
    assert r.json["box_barcode"] == "BOX001"


def test_unassign_tube_from_box(auth_client):
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    tube = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]}).json
    r = auth_client.put(f"/api/tubes/{tube['id']}", json={"barcode": "TUBE001", "box_id": None})
    assert r.status_code == 200
    assert r.json["box_id"] is None


def test_box_tube_count_updates(auth_client):
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]})
    auth_client.post("/api/tubes", json={"barcode": "TUBE002", "box_id": box["id"]})
    r = auth_client.get(f"/api/boxes/{box['id']}")
    assert r.json["tubes"][0]["box_id"] == box["id"]
    assert len(r.json["tubes"]) == 2
