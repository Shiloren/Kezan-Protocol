from fastapi.testclient import TestClient
from kezan.main import app
from kezan.profile_manager import ProfileManager, GameVersion


def test_profile_routes_happy(tmp_path, monkeypatch):
    # Swap the module-level profile_manager to a temp-backed one
    pm = ProfileManager(config_dir=str(tmp_path / "profiles"))
    import kezan.routes.profile_routes as pr
    monkeypatch.setattr(pr, "profile_manager", pm, raising=True)

    client = TestClient(app)

    # Update profile via PUT
    payload = {
        "default_realm": "EU-Server",
        "watched_items": [],
        "price_thresholds": {},
        "notification_enabled": True,
    }
    r = client.put("/api/profile/retail", json=payload)
    assert r.status_code == 200 and r.json()["status"] == "success"

    # Add watched item
    r = client.post("/api/profile/retail/items", json={"itemId": 123, "maxPrice": 50})
    assert r.status_code == 200

    # Update threshold for existing item
    r = client.put("/api/profile/retail/items/123/threshold", json={"maxPrice": 40})
    assert r.status_code == 200

    # Get profile and confirm values
    r = client.get("/api/profile/retail")
    assert r.status_code == 200
    data = r.json()
    assert data["preferences"]["default_realm"] == "EU-Server"
    assert 123 in data["preferences"]["watched_items"]
    assert data["preferences"]["price_thresholds"].get("123") == 40 or \
           data["preferences"]["price_thresholds"].get(123) == 40

    # History should exist (empty list)
    r = client.get("/api/profile/retail/items/123/history")
    assert r.status_code == 200 and "history" in r.json()

    # Remove watched item
    r = client.delete("/api/profile/retail/items/123")
    assert r.status_code == 200
