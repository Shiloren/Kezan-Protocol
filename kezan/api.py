from fastapi import APIRouter
from kezan.analyzer import get_top_items

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
