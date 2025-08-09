from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from kezan.profile_manager import ProfileManager, GameVersion

router = APIRouter(prefix="/api/profile")
profile_manager = ProfileManager()

class ProfilePreferences(BaseModel):
    default_realm: str
    watched_items: List[int]
    price_thresholds: dict[int, int]
    notification_enabled: bool

class WatchedItemRequest(BaseModel):
    itemId: int
    maxPrice: Optional[int] = None

class ThresholdUpdate(BaseModel):
    maxPrice: int

@router.get("/{version}")
async def get_profile(version: str):
    try:
        game_version = GameVersion(version)
        profile = profile_manager.get_profile(game_version)
        return {
            "version": version,
            "preferences": {
                "default_realm": profile.preferences.default_realm,
                "watched_items": profile.preferences.watched_items,
                "price_thresholds": profile.preferences.price_thresholds,
                "notification_enabled": profile.preferences.notification_enabled
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{version}")
async def update_profile(version: str, preferences: ProfilePreferences):
    try:
        game_version = GameVersion(version)
        profile_manager.update_preferences(
            game_version,
            default_realm=preferences.default_realm,
            watched_items=preferences.watched_items,
            price_thresholds=preferences.price_thresholds,
            notification_enabled=preferences.notification_enabled
        )
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{version}/items")
async def add_watched_item(version: str, item: WatchedItemRequest):
    try:
        game_version = GameVersion(version)
        profile_manager.add_watched_item(game_version, item.itemId, item.maxPrice)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{version}/items/{item_id}")
async def remove_watched_item(version: str, item_id: int):
    try:
        game_version = GameVersion(version)
        profile_manager.remove_watched_item(game_version, item_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{version}/items/{item_id}/threshold")
async def update_threshold(version: str, item_id: int, threshold: ThresholdUpdate):
    try:
        game_version = GameVersion(version)
        profile = profile_manager.get_profile(game_version)
        if item_id not in profile.preferences.watched_items:
            raise HTTPException(status_code=404, detail="Item no encontrado")
        
        profile.preferences.price_thresholds[item_id] = threshold.maxPrice
        profile_manager.save_profile(profile)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{version}/items/{item_id}/history")
async def get_price_history(version: str, item_id: int):
    try:
        game_version = GameVersion(version)
        profile = profile_manager.get_profile(game_version)
        history = profile.auction_history.get(item_id, [])
        return {"history": history}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
