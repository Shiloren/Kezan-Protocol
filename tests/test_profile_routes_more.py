from fastapi import FastAPI
from fastapi.testclient import TestClient

from kezan.routes.profile_routes import router

app = FastAPI()
app.include_router(router)


def test_get_profile_invalid_version():
    client = TestClient(app)
    r = client.get("/api/profile/unknown")
    assert r.status_code == 400


def test_add_remove_and_threshold_errors(monkeypatch):
    client = TestClient(app)

    # Add watched item happy path
    r = client.post("/api/profile/retail/items", json={"itemId": 42, "maxPrice": 100})
    assert r.status_code == 200

    # Update threshold for non-existing item -> 404
    r = client.put("/api/profile/retail/items/999/threshold", json={"maxPrice": 50})
    assert r.status_code == 404

    # Remove non-existing item is a 200 (no-op) or handled gracefully
    r = client.delete("/api/profile/retail/items/999")
    assert r.status_code in (200, 400)

    # Update profile with invalid version -> 400
    r = client.put(
        "/api/profile/unknown",
        json={
            "default_realm": "",
            "watched_items": [],
            "price_thresholds": {},
            "notification_enabled": True,
        },
    )
    assert r.status_code == 400
