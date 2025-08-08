"""Economic analysis of crafting recipes."""

from __future__ import annotations

from functools import lru_cache
from typing import Callable, Dict, Iterable, List, Optional, Set

from kezan import cache


def build_analyzer(
    recipes: Iterable[Dict],
    price_lookup: Callable[[int], float],
    scarce: Optional[Set[int]] = None,
):
    """Create a cached recipe analyzer.

    Parameters
    ----------
    recipes:
        Iterable of recipe dictionaries as described in ``recipes.py``.
    price_lookup:
        Callable returning the market price for a given item id.  It may
        raise an exception if the price is unknown.
    scarce:
        Optional set of item IDs that should be penalised (10% markup) when
        calculating reagent costs.
    """

    recipe_map = {r["recipe_id"]: r for r in recipes}
    product_map = {r["product_id"]: r for r in recipes}
    scarce = scarce or set()

    @lru_cache(maxsize=128)
    def _analyze(recipe_id: int, depth: int = 0) -> Dict:
        recipe = recipe_map[recipe_id]
        cost = 0.0
        missing: List[int] = []

        for item_id, qty in recipe.get("reagents", []):
            component_cost: Optional[float] = None
            if item_id in product_map and depth < 1:
                sub = _analyze(product_map[item_id]["recipe_id"], depth + 1)
                produced = product_map[item_id].get("quantity", 1) or 1
                component_cost = sub["cost"] / produced
            else:
                try:
                    component_cost = price_lookup(item_id)
                except Exception:  # pragma: no cover - depends on lookup
                    missing.append(item_id)
                    continue

            if item_id in scarce:
                component_cost *= 1.1
            cost += component_cost * qty

        try:
            sale_price = price_lookup(recipe["product_id"]) * recipe.get("quantity", 1)
        except Exception:  # pragma: no cover - depends on lookup
            sale_price = 0.0

        profit = sale_price - cost
        margin = profit / sale_price if sale_price else 0.0

        result = {
            "recipe_id": recipe_id,
            "product_id": recipe["product_id"],
            "cost": round(cost, 2),
            "sale_price": round(sale_price, 2),
            "profit": round(profit, 2),
            "margin": round(margin, 2),
            "risk": len(missing),
            "missing_reagents": missing,
        }
        processed = cache.get("processed_recipes") or set()
        processed.add(recipe_id)
        cache.set("processed_recipes", processed, ttl=3600)
        return result

    return _analyze


def analyze_recipes(
    recipes: Iterable[Dict],
    price_lookup: Callable[[int], float],
    scarce: Optional[Set[int]] = None,
) -> List[Dict]:
    """Analyze multiple recipes and return their economic metrics."""

    analyzer = build_analyzer(recipes, price_lookup, scarce)
    return [analyzer(r["recipe_id"]) for r in recipes]

