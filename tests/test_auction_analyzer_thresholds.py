import pytest

from kezan.auction_analyzer import AuctionAnalyzer
from kezan.profile_manager import GameVersion


class DummyBlizz:
    async def get_auctions(self, realm: str):  # returns minimal auctions
        return [
            {"item": {"id": 101}, "unit_price": 5, "quantity": 1},
            {"item": {"id": 102}, "unit_price": 50, "quantity": 1},
        ]


@pytest.mark.asyncio
async def test_monitor_price_thresholds_alerts(monkeypatch):
    aa = AuctionAnalyzer()
    # Replace blizzard api
    aa.blizzard_api = DummyBlizz()
    # Prepare profile with thresholds
    prof = aa.profile_manager.get_profile(GameVersion.RETAIL)
    prof.preferences.watched_items = [101, 102]
    prof.preferences.price_thresholds = {101: 10, 102: 40}
    aa.profile_manager.save_profile(prof)

    alerts = await aa.monitor_price_thresholds(GameVersion.RETAIL, realm="x")
    # Item 101 should trigger, 102 should not
    assert any(a["item_id"] == 101 for a in alerts)
    assert not any(a["item_id"] == 102 for a in alerts)
