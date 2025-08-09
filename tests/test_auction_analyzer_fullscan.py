import asyncio
import pytest

from kezan.auction_analyzer import AuctionAnalyzer
from kezan.profile_manager import GameVersion


class DummyLLM:
    async def scan_auction_house(self, current_data, profile_preferences, game_version):
        # Return one opportunity to exercise history update path
        return [{"item_id": 1, "price": 10, "quantity": 1}]


class DummyBlizz:
    async def get_auctions(self, realm):
        return []


@pytest.mark.asyncio
async def test_full_scan_one_iteration(monkeypatch):
    az = AuctionAnalyzer()
    az.llm = DummyLLM()
    az.blizzard_api = DummyBlizz()

    # Run only once by cancelling after first sleep
    async def fake_sleep(_):
        raise asyncio.CancelledError()

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    with pytest.raises(asyncio.CancelledError):
        await az.full_scan(GameVersion.RETAIL, realm="R", scan_interval=0)
