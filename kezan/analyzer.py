"""Módulo para analizar items de subasta."""

from kezan.blizzard_api import fetch_auction_data
from kezan.formatter import format_for_ai
from kezan.logger import get_logger
from kezan import cache

logger = get_logger(__name__)

async def get_top_items(limit: int = 5, min_margin: float = 0.3):
    """Obtiene los items de subasta con mayor margen.

    Parámetros:
    - limit (int): número máximo de items a devolver.
    - min_margin (float): margen mínimo requerido para incluir un item.

    Retorna:
    - dict: diccionario con los items principales o un mensaje de error.
    """
    cache_key = f"top_items_{limit}_{min_margin}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        data = await fetch_auction_data()
    except RuntimeError as e:
        return {"error": str(e)}

    if not data:
        return {"error": "No se pudieron obtener los datos de subasta."}

    auctions = data.get("auctions", [])
    items = []
    for entry in auctions:
        item_id = entry.get("item", {}).get("id")
        if not item_id:
            logger.warning("Entrada sin item ID: %s", entry)
            continue

        buyout = entry.get("buyout") or 0
        unit_price = buyout / entry.get("quantity", 1)
        avg_price = unit_price * 1.5  # Simulación de beneficio
        margin = (avg_price - unit_price) / avg_price

        if margin >= min_margin:
            items.append({
                "name": f"ItemID {item_id}",
                "ah_price": unit_price,
                "avg_sell_price": avg_price,
                "margin": round(margin, 2),
            })
    result = format_for_ai(items[:limit])
    cache.set(cache_key, result, ttl=300)
    return result
