from fastapi import APIRouter
from kezan.analyzer import get_top_items
from kezan.llm_interface import analyze_items_with_llm

router = APIRouter(prefix="/api", tags=["Kezan Protocol"])

@router.get("/gangas")
async def gangas_top(limit: int = 5, min_margin: float = 0.3):
    """
    Endpoint to retrieve a list of top auction items based on margin filters.

    :param limit: Maximum number of items to return.
    :param min_margin: Minimum margin required for an item to be included.
    :return: A list of items in JSON format, or an error dict if the Blizzard API is not configured.
    """
    return await get_top_items(limit=limit, min_margin=min_margin)


@router.get("/consejo")
async def consejo(limit: int = 5, min_margin: float = 0.3):
    """Generate a recommendation based on top auction items."""
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
