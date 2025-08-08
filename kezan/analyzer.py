def get_top_items(limit=5, min_margin=0.3):
    sample_data = [
        {"name": "Black Lotus", "ah_price": 92, "avg_sell_price": 145, "margin": 0.57},
        {"name": "Greater Fire Protection Potion", "ah_price": 3, "avg_sell_price": 5, "margin": 0.4},
    ]
    return [item for item in sample_data if item["margin"] >= min_margin][:limit]
