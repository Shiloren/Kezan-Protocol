from fastapi import APIRouter
from kezan.analyzer import get_top_items

router = APIRouter(prefix="/api", tags=["Kezan Protocol"])

@router.get("/gangas")
async def gangas_top(limit: int = 5, min_margin: float = 0.3):
    return await get_top_items(limit=limit, min_margin=min_margin)
