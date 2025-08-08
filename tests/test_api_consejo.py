import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import kezan.api as api_module
from main import app

client = TestClient(app)


def test_consejo_success(monkeypatch):
    async def fake_get_top_items(limit=5, min_margin=0.3):
        return {"items": [{"name": "Black Lotus"}]}

    def fake_analyze_items_with_llm(data):
        return "Compra Black Lotus"

    monkeypatch.setattr(api_module, "get_top_items", fake_get_top_items)
    monkeypatch.setattr(api_module, "analyze_items_with_llm", fake_analyze_items_with_llm)

    response = client.get("/api/consejo")
    assert response.status_code == 200
    assert response.json() == {
        "recomendacion": "Compra Black Lotus",
        "items": [{"name": "Black Lotus"}],
    }


def test_consejo_model_error(monkeypatch):
    async def fake_get_top_items(limit=5, min_margin=0.3):
        return {"items": [{"name": "Black Lotus"}]}

    def fake_analyze_items_with_llm(data):
        raise RuntimeError("El modelo de IA local no está activo o no responde.")

    monkeypatch.setattr(api_module, "get_top_items", fake_get_top_items)
    monkeypatch.setattr(api_module, "analyze_items_with_llm", fake_analyze_items_with_llm)

    response = client.get("/api/consejo")
    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "El modelo de IA local no está activo o no responde."
    assert data["items"] == [{"name": "Black Lotus"}]


def test_consejo_summary_error(monkeypatch):
    async def fake_get_top_items(limit=5, min_margin=0.3):
        return {"error": "No se pudieron obtener los datos de subasta."}

    monkeypatch.setattr(api_module, "get_top_items", fake_get_top_items)

    response = client.get("/api/consejo")
    assert response.status_code == 200
    assert response.json()["error"] == "No se pudieron obtener los datos de subasta."
