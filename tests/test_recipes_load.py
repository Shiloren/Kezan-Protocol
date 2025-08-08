"""Pruebas para carga de recetas y mapeos."""

import json
import httpx
import pytest

from kezan import recipes


def test_load_recipes_local(tmp_path):
    """Carga desde un archivo JSON local."""
    datos = {"alquimia": [{"recipe_id": 1, "product_id": 2, "quantity": 1, "reagents": [], "profession": "alquimia", "level_required": 1}]}
    archivo = tmp_path / "recetas.json"
    archivo.write_text(json.dumps(datos))
    res = recipes.load_recipes("alquimia", str(archivo))
    assert res[0]["recipe_id"] == 1


def test_load_recipes_api(monkeypatch):
    """Obtiene recetas desde la API simulada."""
    monkeypatch.setattr(recipes, "API_CLIENT_ID", "id")
    monkeypatch.setattr(recipes, "API_CLIENT_SECRET", "sec")

    def fake_get(*a, **k):
        class R:
            def raise_for_status(self):
                pass

            def json(self):
                return {"recipes": [{"recipe_id": 5, "product_id": 7, "quantity": 1, "reagents": [], "profession": "alquimia", "level_required": 1}]}
        return R()

    monkeypatch.setattr(httpx, "get", fake_get)
    res = recipes.load_recipes("alquimia")
    assert res[0]["recipe_id"] == 5


def test_load_recipes_no_credentials(monkeypatch):
    """Falla si no hay credenciales para la API."""
    recipes.load_recipes.cache_clear()
    monkeypatch.setattr(recipes, "API_CLIENT_ID", "")
    monkeypatch.setattr(recipes, "API_CLIENT_SECRET", "")
    with pytest.raises(RuntimeError):
        recipes.load_recipes("herboristeria")


def test_build_recipe_maps():
    """Genera mapeos por receta y producto."""
    data = [{"recipe_id": 1, "product_id": 2}, {"recipe_id": 3, "product_id": 4}]
    by_recipe, by_product = recipes.build_recipe_maps(data)
    assert by_recipe[1]["product_id"] == 2
    assert by_product[4]["recipe_id"] == 3
