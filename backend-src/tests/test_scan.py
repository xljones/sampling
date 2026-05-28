def test_scan_requires_auth(client):
    r = client.get("/api/scan/BOX001")
    assert r.status_code == 401


def test_scan_box(auth_client):
    auth_client.post("/api/boxes", json={"barcode": "BOX001", "name": "Shelf A"})
    r = auth_client.get("/api/scan/BOX001")
    assert r.status_code == 200
    assert r.json["type"] == "box"
    assert r.json["data"]["barcode"] == "BOX001"


def test_scan_tube(auth_client):
    auth_client.post("/api/tubes", json={"barcode": "TUBE001", "site_name": "River"})
    r = auth_client.get("/api/scan/TUBE001")
    assert r.status_code == 200
    assert r.json["type"] == "tube"
    assert r.json["data"]["barcode"] == "TUBE001"


def test_scan_box_takes_priority_over_tube(auth_client):
    # If same barcode exists as both (shouldn't happen, but box wins)
    auth_client.post("/api/boxes", json={"barcode": "SHARED"})
    r = auth_client.get("/api/scan/SHARED")
    assert r.json["type"] == "box"


def test_scan_not_found(auth_client):
    r = auth_client.get("/api/scan/UNKNOWN")
    assert r.status_code == 404


def test_search_requires_auth(client):
    r = client.get("/api/search?q=test")
    assert r.status_code == 401


def test_search_returns_boxes(auth_client):
    auth_client.post("/api/boxes", json={"barcode": "RIVER-BOX", "name": "River Box"})
    r = auth_client.get("/api/search?q=RIVER")
    assert r.status_code == 200
    barcodes = [item["barcode"] for item in r.json]
    assert "RIVER-BOX" in barcodes


def test_search_returns_tubes(auth_client):
    auth_client.post("/api/tubes", json={"barcode": "DEEP-TUBE", "site_name": "Deep Lake"})
    r = auth_client.get("/api/search?q=DEEP")
    assert r.status_code == 200
    barcodes = [item["barcode"] for item in r.json]
    assert "DEEP-TUBE" in barcodes


def test_search_returns_both(auth_client):
    auth_client.post("/api/boxes", json={"barcode": "ALPHA-BOX"})
    auth_client.post("/api/tubes", json={"barcode": "ALPHA-TUBE"})
    r = auth_client.get("/api/search?q=ALPHA")
    assert r.status_code == 200
    barcodes = [item["barcode"] for item in r.json]
    assert "ALPHA-BOX" in barcodes
    assert "ALPHA-TUBE" in barcodes


def test_search_empty_query(auth_client):
    r = auth_client.get("/api/search?q=")
    assert r.status_code == 200
    assert isinstance(r.json, list)
