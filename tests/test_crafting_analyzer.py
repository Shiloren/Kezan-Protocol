import os
import sys

import kezan.crafting_analyzer as ca

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_analyze_recipe_with_subrecipe():
    recipes = [
        {
            "recipe_id": 1,
            "product_id": 101,
            "quantity": 1,
            "reagents": [(201, 2), (202, 1)],
            "profession": "alchemy",
            "level_required": 1,
        },
        {
            "recipe_id": 2,
            "product_id": 201,
            "quantity": 2,
            "reagents": [(301, 1)],
            "profession": "alchemy",
            "level_required": 1,
        },
    ]

    prices = {202: 5, 301: 3, 101: 20}

    calls = []

    def price_lookup(item_id: int) -> float:
        calls.append(item_id)
        return prices[item_id]

    analyzer = ca.build_analyzer(recipes, price_lookup)
    result = analyzer(1)
    assert result["cost"] == 8.0
    assert result["profit"] == 12.0
    assert result["margin"] == 0.6

    first_calls = len(calls)
    analyzer(1)
    # cached result should not trigger additional lookups
    assert len(calls) == first_calls


def test_analyze_recipe_missing_reagent():
    recipes = [
        {
            "recipe_id": 1,
            "product_id": 101,
            "quantity": 1,
            "reagents": [(202, 1)],
            "profession": "alchemy",
            "level_required": 1,
        }
    ]

    prices = {101: 20}

    def price_lookup(item_id: int) -> float:
        return prices[item_id]

    analyzer = ca.build_analyzer(recipes, price_lookup)
    result = analyzer(1)
    assert result["missing_reagents"] == [202]
