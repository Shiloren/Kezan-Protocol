"""Prueba de recetas con materiales faltantes."""

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

