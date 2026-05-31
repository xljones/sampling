from flask.testing import FlaskClient


def test_list_tubes_requires_auth(client: FlaskClient) -> None:
    assert client.get("/api/tubes").status_code == 401


def test_list_tubes(auth_client: FlaskClient) -> None:
    auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    r = auth_client.get("/api/tubes")
    assert r.status_code == 200
    assert len(r.json) == 1


def test_create_tube(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    assert r.status_code == 201
    assert r.json["barcode"] == "TUBE001"
    assert r.json["box_id"] is None


def test_create_tube_with_box(auth_client: FlaskClient) -> None:
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]})
    assert r.status_code == 201
    assert r.json["box_id"] == box["id"]
    assert r.json["box_barcode"] == "BOX001"


def test_create_tube_with_core(auth_client: FlaskClient) -> None:
    core = auth_client.post("/api/cores", json={"barcode": "CORE001"}).json
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "core_id": core["id"]})
    assert r.status_code == 201
    assert r.json["core_id"] == core["id"]


def test_create_tube_missing_barcode(auth_client: FlaskClient) -> None:
    assert auth_client.post("/api/tubes", json={"site_name": "Lake"}).status_code == 400


def test_create_tube_duplicate_barcode(auth_client: FlaskClient) -> None:
    auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    assert auth_client.post("/api/tubes", json={"barcode": "TUBE001"}).status_code == 409


def test_get_tube(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "site_name": "River A"})
    tube_id = r.json["id"]
    r = auth_client.get(f"/api/tubes/{tube_id}")
    assert r.status_code == 200
    assert r.json["site_name"] == "River A"


def test_get_tube_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.get("/api/tubes/999").status_code == 404


def test_update_tube(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "site_name": "Old Site"})
    tube_id = r.json["id"]
    r = auth_client.put(f"/api/tubes/{tube_id}", json={"barcode": "TUBE001", "site_name": "New Site"})
    assert r.status_code == 200
    assert r.json["site_name"] == "New Site"


def test_update_tube_missing_barcode(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    tube_id = r.json["id"]
    assert auth_client.put(f"/api/tubes/{tube_id}", json={"site_name": "No barcode"}).status_code == 400


def test_update_tube_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.put("/api/tubes/999", json={"barcode": "TUBE001"}).status_code == 404


def test_update_tube_duplicate_barcode(auth_client: FlaskClient) -> None:
    auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE002"})
    tube_id = r.json["id"]
    assert auth_client.put(f"/api/tubes/{tube_id}", json={"barcode": "TUBE001"}).status_code == 409


def test_delete_tube(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/tubes", json={"barcode": "TUBE001"})
    tube_id = r.json["id"]
    assert auth_client.delete(f"/api/tubes/{tube_id}").status_code == 204
    assert auth_client.get(f"/api/tubes/{tube_id}").status_code == 404


def test_delete_tube_not_found(auth_client: FlaskClient) -> None:
    assert auth_client.delete("/api/tubes/999").status_code == 404


def test_assign_tube_to_box(auth_client: FlaskClient) -> None:
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    tube = auth_client.post("/api/tubes", json={"barcode": "TUBE001"}).json
    r = auth_client.put(f"/api/tubes/{tube['id']}", json={"barcode": "TUBE001", "box_id": box["id"]})
    assert r.status_code == 200
    assert r.json["box_id"] == box["id"]


def test_unassign_tube_from_box(auth_client: FlaskClient) -> None:
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    tube = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]}).json
    r = auth_client.put(f"/api/tubes/{tube['id']}", json={"barcode": "TUBE001", "box_id": None})
    assert r.status_code == 200
    assert r.json["box_id"] is None


def test_bulk_assign_tubes(auth_client: FlaskClient) -> None:
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    t1 = auth_client.post("/api/tubes", json={"barcode": "TUBE001"}).json
    t2 = auth_client.post("/api/tubes", json={"barcode": "TUBE002"}).json
    r = auth_client.post("/api/tubes/bulk-assign", json={
        "tube_ids": [t1["id"], t2["id"]], "box_id": box["id"]
    })
    assert r.status_code == 200
    assert r.json["assigned"] == 2


def test_bulk_assign_tubes_missing_fields(auth_client: FlaskClient) -> None:
    r = auth_client.post("/api/tubes/bulk-assign", json={"tube_ids": [1]})
    assert r.status_code == 400


def test_bulk_assign_tubes_empty_list(auth_client: FlaskClient) -> None:
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    r = auth_client.post("/api/tubes/bulk-assign", json={"tube_ids": [], "box_id": box["id"]})
    assert r.status_code == 400


def test_tube_history(auth_client: FlaskClient) -> None:
    tube = auth_client.post("/api/tubes", json={"barcode": "TUBE001"}).json
    r = auth_client.get(f"/api/tubes/{tube['id']}/history")
    assert r.status_code == 200
    assert isinstance(r.json, list)
    assert len(r.json) >= 1


def test_revert_tube(auth_client: FlaskClient) -> None:
    tube = auth_client.post("/api/tubes", json={"barcode": "TUBE001", "site_name": "Original"}).json
    auth_client.put(f"/api/tubes/{tube['id']}", json={"barcode": "TUBE001", "site_name": "Changed"})
    history = auth_client.get(f"/api/tubes/{tube['id']}/history").json
    first_version = history[-1]
    r = auth_client.post(f"/api/tubes/{tube['id']}/revert/{first_version['id']}")
    assert r.status_code == 200
    assert r.json["site_name"] == "Original"


def test_revert_tube_not_found(auth_client: FlaskClient) -> None:
    tube = auth_client.post("/api/tubes", json={"barcode": "TUBE001"}).json
    assert auth_client.post(f"/api/tubes/{tube['id']}/revert/9999").status_code == 404


def test_box_tube_count_updates(auth_client: FlaskClient) -> None:
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]})
    auth_client.post("/api/tubes", json={"barcode": "TUBE002", "box_id": box["id"]})
    r = auth_client.get(f"/api/boxes/{box['id']}")
    assert r.json["tubes"][0]["box_id"] == box["id"]
    assert len(r.json["tubes"]) == 2
