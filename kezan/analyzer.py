from kezan.blizzard_api import fetch_auction_data
from kezan.formatter import format_for_ai
from kezan.logger import get_logger
from kezan import cache

logger = get_logger(__name__)

async def get_top_items(limit=5, min_margin=0.3):
    """
    Retrieves the top auction items with margins above ``min_margin``.

    If the Blizzard API is not configured via environment variables,
    a RuntimeError will be caught and a dictionary with an "error"
    message will be returned instead.

    :param limit: Maximum number of items to return.
    :param min_margin: Minimum margin required for an item to be included.
    :return: A list of dictionaries representing the top items or an error dict.
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
