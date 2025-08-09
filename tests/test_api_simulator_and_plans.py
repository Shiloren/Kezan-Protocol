import json
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_simulate_endpoint_returns_baseline_when_no_history():
    resp = client.post("/api/simulate", json={"strategy": "RULE 'demo' WHEN TRUE THEN SKIP('x')"})
    assert resp.status_code == 200
    data = resp.json()
    assert set(["roi", "volatility", "est_time_to_sell_h", "trades", "notes"]).issubset(data.keys())
    assert data["trades"] == 0 or data["trades"] >= 0


def test_premium_check_endpoint_behaviour():
    # Free plan when no api_key
    r1 = client.get("/api/premium-check")
    assert r1.status_code == 200
    assert r1.json().get("plan") == "Free"

    # Pro when api_key provided (placeholder logic)
    r2 = client.get("/api/premium-check", params={"api_key": "abc"})
    assert r2.status_code == 200
    assert r2.json().get("plan") == "Pro"
