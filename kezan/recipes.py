"""Utilities for loading profession recipes.

This module can load recipe data from a local JSON file or, if properly
configured, fetch it from the official Blizzard API.  Each recipe is
represented as a dictionary with the following keys::

    {
        "recipe_id": int,
        "product_id": int,
        "quantity": int,
        "reagents": [(item_id, qty), ...],
        "profession": str,
        "level_required": int,
    }

The module provides lightweight helpers used by the crafting analyzer to
evaluate the profitability of crafting different items.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

import httpx

from kezan.config import API_CLIENT_ID, API_CLIENT_SECRET, REGION


@lru_cache(maxsize=32)
def load_recipes(profesion: str, json_file: str | None = None) -> List[Dict]:
    """Load recipes for ``profesion``.

    Parameters
    ----------
    profesion:
        Name of the profession to load.
    json_file:
        Optional path to a local JSON file containing recipe data.  When
        provided, no remote requests are performed.

    Returns
    -------
    List[Dict]
        List of recipe dictionaries.

    Raises
    ------
    RuntimeError
        If the data cannot be retrieved.
    """

    if json_file:
        data = json.loads(Path(json_file).read_text())
        return data.get(profesion, [])

    if not API_CLIENT_ID or not API_CLIENT_SECRET:
        raise RuntimeError("Las claves de la API de Blizzard no están configuradas.")

    url = f"https://{REGION}.api.blizzard.com/data/wow/profession/{profesion}/recipes"
    try:
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("recipes", [])
    except Exception as exc:  # pragma: no cover - network errors
        raise RuntimeError("No se pudieron obtener las recetas de Blizzard") from exc


def build_recipe_maps(recipes: List[Dict]) -> Tuple[Dict[int, Dict], Dict[int, Dict]]:
    """Return mappings for quick recipe lookup.

    Returns two dictionaries: one indexed by ``recipe_id`` and another by
    ``product_id``.
    """

    by_recipe_id = {r["recipe_id"]: r for r in recipes}
    by_product_id = {r["product_id"]: r for r in recipes}
    return by_recipe_id, by_product_id

