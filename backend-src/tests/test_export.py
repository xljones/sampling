import re


def test_export_tubes_requires_auth(client):
    r = client.get("/api/export/tubes")
    assert r.status_code == 401


def test_export_boxes_requires_auth(client):
    r = client.get("/api/export/boxes")
    assert r.status_code == 401


def test_export_tubes_csv(auth_client):
    auth_client.post("/api/tubes", json={"barcode": "TUBE001", "site_name": "River A"})
    r = auth_client.get("/api/export/tubes")
    assert r.status_code == 200
    assert "text/csv" in r.content_type
    disposition = r.headers["Content-Disposition"]
    assert re.search(r'filename="tubes-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.csv"', disposition)
    text = r.data.decode()
    assert "barcode" in text
    assert "TUBE001" in text
    assert "River A" in text


def test_export_tubes_includes_box_info(auth_client):
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001", "name": "Shelf A"}).json
    auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]})
    r = auth_client.get("/api/export/tubes")
    text = r.data.decode()
    assert "BOX001" in text
    assert "Shelf A" in text


def test_export_tubes_empty(auth_client):
    r = auth_client.get("/api/export/tubes")
    assert r.status_code == 200
    lines = r.data.decode().strip().splitlines()
    assert len(lines) == 1  # header only


def test_export_boxes_csv(auth_client):
    auth_client.post("/api/boxes", json={"barcode": "BOX001", "name": "Shelf A", "location": "Freezer 2"})
    r = auth_client.get("/api/export/boxes")
    assert r.status_code == 200
    assert "text/csv" in r.content_type
    disposition = r.headers["Content-Disposition"]
    assert re.search(r'filename="boxes-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.csv"', disposition)
    text = r.data.decode()
    assert "barcode" in text
    assert "BOX001" in text
    assert "Shelf A" in text


def test_export_boxes_tube_count(auth_client):
    box = auth_client.post("/api/boxes", json={"barcode": "BOX001"}).json
    auth_client.post("/api/tubes", json={"barcode": "TUBE001", "box_id": box["id"]})
    auth_client.post("/api/tubes", json={"barcode": "TUBE002", "box_id": box["id"]})
    r = auth_client.get("/api/export/boxes")
    text = r.data.decode()
    assert "2" in text
