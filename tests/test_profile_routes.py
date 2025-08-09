from fastapi.testclient import TestClient

from kezan.main import app


def test_profile_routes_smoke(monkeypatch):
    client = TestClient(app)

    # GET profile invalid version
    r = client.get("/api/profile/invalid")
    assert r.status_code == 400

    # Try a plausible enum value
    r = client.get("/api/profile/retail")
    assert r.status_code in (200, 400)

    # POST add item (soft check)
    r2 = client.post("/api/profile/retail/items", json={"itemId": 1, "maxPrice": 10})
    assert r2.status_code in (200, 400)

    # PUT threshold update path existence
    r3 = client.put("/api/profile/retail/items/1/threshold", json={"maxPrice": 5})
    assert r3.status_code in (200, 400, 404)
