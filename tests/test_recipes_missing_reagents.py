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
    # Configurar una receta con un reactivo escaso (ID 99) y cantidad 1
    recipes = [{"recipe_id": 1, "product_id": 10, "quantity": 1, "reagents": [(99, 1)]}]

    # La función lookup devuelve un precio base para cualquier reactivo
    def lookup(item_id: int) -> float:
        return 10.0

    # Indicar que el reactivo 99 es escaso mediante el parámetro 'scarce'
    result = analyze_recipes(recipes, lookup, scarce={99})[0]

    # El costo debe incrementarse en 1.0 debido a la escasez, pasando de 10.0 a 11.0
    assert result["cost"] == 11.0

