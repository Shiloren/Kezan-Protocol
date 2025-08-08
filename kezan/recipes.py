"""Utilidades para cargar recetas de profesiones.

Puede cargar datos desde un JSON local o, si está configurado, desde la API de
Blizzard. Cada receta se representa como::

    {
        "recipe_id": int,
        "product_id": int,
        "quantity": int,
        "reagents": [(item_id, qty), ...],
        "profession": str,
        "level_required": int,
    }

El módulo ofrece helpers ligeros usados por el analizador de crafteo para
evaluar la rentabilidad de distintas recetas.
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
    """Carga las recetas para ``profesion``.

    Parámetros:
    - profesion (str): nombre de la profesión.
    - json_file (str | None): ruta opcional a JSON local con datos.

    Retorna:
    - List[Dict]: listado de recetas.

    Lanza:
    - RuntimeError: si los datos no pueden recuperarse.
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
    """Retorna mapeos para búsqueda rápida de recetas.

    Devuelve dos diccionarios: uno indexado por ``recipe_id`` y otro por
    ``product_id``.
    """
    by_recipe_id = {r["recipe_id"]: r for r in recipes}
    by_product_id = {r["product_id"]: r for r in recipes}
    return by_recipe_id, by_product_id

