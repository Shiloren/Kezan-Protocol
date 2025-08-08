"""Pruebas para las rutas de la API."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from kezan import api


app = FastAPI()
app.include_router(api.router)


def test_gangas_top(monkeypatch):
    """Cubre la ruta /gangas."""
    async def fake_get_top_items(limit: int, min_margin: float):
        return {"items": []}

    monkeypatch.setattr(api, "get_top_items", fake_get_top_items)
    client = TestClient(app)
    resp = client.get("/api/gangas")
    assert resp.status_code == 200


def test_crafteables_error(monkeypatch):
    """Cubre la ruta /crafteables cuando el LLM falla."""
    monkeypatch.setattr(api, "load_recipes", lambda p: [{}])

    def fake_analyze_recipes(recipes, price_lookup):
        try:
            price_lookup(1)
        except KeyError:
            pass
        return [{"profit": 0}]

    monkeypatch.setattr(api, "analyze_recipes", fake_analyze_recipes)
    monkeypatch.setattr(api, "analyze_recipes_with_llm", lambda r: (_ for _ in ()).throw(RuntimeError("falla")))
    client = TestClient(app)
    resp = client.get("/api/crafteables?profesion=alc")
    assert resp.json()["error"] == "falla"
