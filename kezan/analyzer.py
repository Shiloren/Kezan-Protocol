from kezan.blizzard_api import fetch_auction_data


async def get_top_items(limit=5, min_margin=0.3):
    try:
        data = await fetch_auction_data()
    except RuntimeError as e:
        return {"error": str(e)}

    auctions = data.get("auctions", [])

    items = []
    for entry in auctions:
        buyout = entry.get("buyout") or 0
        unit_price = buyout / entry.get("quantity", 1)
        avg_price = unit_price * 1.5  # Simulación de beneficio
        margin = (avg_price - unit_price) / avg_price

        if margin >= min_margin:
            items.append({
                "name": f"ItemID {entry['item']['id']}",
                "ah_price": unit_price,
                "avg_sell_price": avg_price,
                "margin": round(margin, 2),
            })

    return items[:limit]
