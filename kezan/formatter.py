"""Ayudantes para preparar datos de items para modelos de lenguaje."""

from kezan.item_resolver import resolve_item_name


def format_for_ai(items: list) -> dict:
    """Prepara datos de items para consumo por LLM.

    Garantiza nombres legibles utilizando un resolvedor que consulta la API de
    Blizzard cuando es necesario.
    """
    return {
        "items": [
            {
                "name": item.get("name") or resolve_item_name(item.get("id")),
                "ah_price": round(item.get("ah_price", 0), 2),
                "avg_sell_price": round(item.get("avg_sell_price", 0), 2),
                "stack_size": item.get("stack_size", 1),
                "estimated_margin": f"{int(item.get('margin', 0) * 100)}%",
            }
            for item in items
        ]
    }
