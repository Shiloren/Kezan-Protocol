import json
import os
import sys
from pathlib import Path

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import kezan.recipes as recipes_module


def test_load_recipes_from_json(tmp_path):
    data = {
        "cocina": [
            {
                "recipe_id": 1,
                "product_id": 10,
                "quantity": 1,
                "reagents": [(20, 2)],
                "profession": "cocina",
                "level_required": 1,
            }
        ]
    }
    file = tmp_path / "recipes.json"
    file.write_text(json.dumps(data))

    recipes_module.load_recipes.cache_clear()
    recs = recipes_module.load_recipes("cocina", json_file=str(file))
    assert recs[0]["product_id"] == 10


def test_load_recipes_caches(monkeypatch, tmp_path):
    data = {"cocina": []}
    file = tmp_path / "recipes.json"
    file.write_text(json.dumps(data))

    calls = {"count": 0}

    original_read_text = Path.read_text

    def fake_read_text(self):
        calls["count"] += 1
        return original_read_text(self)

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    recipes_module.load_recipes.cache_clear()
    recipes_module.load_recipes("cocina", json_file=str(file))
    recipes_module.load_recipes("cocina", json_file=str(file))

    assert calls["count"] == 1
