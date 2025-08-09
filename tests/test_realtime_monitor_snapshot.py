import asyncio
from datetime import datetime, timedelta

import pytest

from kezan.realtime_monitor import RealTimeAuctionMonitor


class DummyAPI:
    async def get_auctions(self, realm):
        return [
            {"item": {"id": 1}, "unit_price": 10, "quantity": 2, "time_left": "LONG"},
            {"item": {"id": 1}, "unit_price": 10, "quantity": 3, "time_left": "LONG"},
            {"item": {"id": 2}, "unit_price": 5,  "quantity": 1, "time_left": "SHORT"},
        ]


@pytest.mark.asyncio
async def test_snapshot_has_age_and_timestamp(monkeypatch):
    mon = RealTimeAuctionMonitor()
    # Speed up interval
    mon.update_interval = 0
    await mon.update_auction_data(DummyAPI(), "x")
    # simulate older last_update to ensure age_seconds > 0
    mon.last_update = mon.last_update - timedelta(seconds=2)
    snap = mon.get_market_snapshot([1, 2])
    assert 1 in snap and 2 in snap
    assert snap[1]["age_seconds"] >= 0
    assert isinstance(snap[1]["timestamp"], str)
