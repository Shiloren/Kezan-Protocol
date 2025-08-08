"""Rutas de la API de Kezan Protocol."""

from fastapi import APIRouter
from kezan.analyzer import get_top_items
from kezan.llm_interface import analyze_items_with_llm, analyze_recipes_with_llm
from kezan.recipes import load_recipes
from kezan.crafting_analyzer import analyze_recipes

router = APIRouter(prefix="/api", tags=["Kezan Protocol"])

@router.get("/gangas")
async def gangas_top(limit: int = 5, min_margin: float = 0.3):
    """Obtiene items de subasta con mayor margen."""
    return await get_top_items(limit=limit, min_margin=min_margin)


@router.get("/consejo")
async def consejo(limit: int = 5, min_margin: float = 0.3):
    """Genera recomendación basada en items de subasta."""
    summary = await get_top_items(limit=limit, min_margin=min_margin)
    if isinstance(summary, dict) and summary.get("error"):
        return summary
    items = summary.get("items", [])
    try:
        recommendation = analyze_items_with_llm(items)
        return {"recomendacion": recommendation, "items": items}
    except RuntimeError as exc:
        # Return the items even if the LLM is not available
        return {"error": str(exc), "items": items}


@router.get("/crafteables")
async def crafteables(profesion: str, min_profit: float = 0.0, limit: int = 5):
    """Devuelve recetas rentables para una profesión."""
    try:
        recipes = load_recipes(profesion)
    except RuntimeError as exc:
        return {"error": str(exc)}

    # Placeholder price lookup; in real usage this should query market data
    def _price_lookup(item_id: int) -> float:
        raise KeyError(item_id)

    analyses = analyze_recipes(recipes, _price_lookup)
    profitable = [a for a in analyses if a["profit"] >= min_profit][:limit]
    try:
        advice = analyze_recipes_with_llm(profitable)
        return {"recomendacion": advice, "recetas": profitable}
    except RuntimeError as exc:
        return {"error": str(exc), "recetas": profitable}
