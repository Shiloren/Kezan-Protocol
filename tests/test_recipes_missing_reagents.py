"""Pruebas de recetas con materiales faltantes y reactivos escasos."""

from kezan.crafting_analyzer import analyze_recipes


def test_recipes_with_missing_reagents():
    """Verifica que los reactivos faltantes se registran correctamente."""

    recipes = [
        {"recipe_id": 1, "product_id": 10, "quantity": 1, "reagents": [(99, 2)]}
    ]

    def lookup(item_id: int) -> float:
        raise KeyError(item_id)

    result = analyze_recipes(recipes, lookup)[0]
    assert result["missing_reagents"] == [99]


def test_scarce_reagent_increases_cost():
    """Un reactivo escaso incrementa el costo total."""
    recipes = [{"recipe_id": 1, "product_id": 10, "quantity": 1, "reagents": [(99, 1)]}]

    def lookup(item_id: int) -> float:
        return 10.0

    result = analyze_recipes(recipes, lookup, scarce={99})[0]
    assert result["cost"] == 11.0

