def format_for_ai(items: list) -> dict:
    return {
        "items": [
            {
                "name": item.get("name", f"ItemID {item.get('id', 'Unknown')}") ,
                "ah_price": round(item.get("ah_price", 0), 2),
                "avg_sell_price": round(item.get("avg_sell_price", 0), 2),
                "stack_size": item.get("stack_size", 1),
                "estimated_margin": f"{int(item.get('margin', 0) * 100)}%"
            }
            for item in items
        ]
    }
