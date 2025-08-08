import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import kezan.api as api_module
from main import app

client = TestClient(app)


def test_crafteables_success(monkeypatch):
    def fake_load_recipes(profesion):
        return [
            {
                "recipe_id": 1,
                "product_id": 101,
                "quantity": 1,
                "reagents": [],
                "profession": profesion,
                "level_required": 1,
            }
        ]

    def fake_analyze_recipes(recipes, price_lookup):
        return [
            {
                "recipe_id": 1,
                "product_id": 101,
                "cost": 1.0,
                "sale_price": 5.0,
                "profit": 4.0,
                "margin": 0.8,
                "risk": 0,
                "missing_reagents": [],
            }
        ]

    def fake_llm(recipes, inventory=None):
        return "Haz este craft"

    monkeypatch.setattr(api_module, "load_recipes", fake_load_recipes)
    monkeypatch.setattr(api_module, "analyze_recipes", fake_analyze_recipes)
    monkeypatch.setattr(api_module, "analyze_recipes_with_llm", fake_llm)

    response = client.get("/api/crafteables", params={"profesion": "cocina"})
    assert response.status_code == 200
    data = response.json()
    assert data["recomendacion"] == "Haz este craft"
    assert data["recetas"][0]["profit"] == 4.0


def test_crafteables_error(monkeypatch):
    def fake_load_recipes(profesion):
        raise RuntimeError("fallo")

    monkeypatch.setattr(api_module, "load_recipes", fake_load_recipes)

    response = client.get("/api/crafteables", params={"profesion": "cocina"})
    assert response.status_code == 200
    assert response.json()["error"] == "fallo"
