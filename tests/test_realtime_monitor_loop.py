import asyncio
import pytest

from kezan.realtime_monitor import RealTimeAuctionMonitor


class DummyBlizzard:
    async def get_auctions(self, realm: str):
        return [{"item": {"id": 5}, "unit_price": 7, "quantity": 1}]


@pytest.mark.asyncio
async def test_realtime_start_stop_one_loop(monkeypatch):
    mon = RealTimeAuctionMonitor()
    dummy = DummyBlizzard()

    async def wrapped_update(blizz, realm):
        # call real method then stop
        ok = await RealTimeAuctionMonitor.update_auction_data(mon, blizz, realm)
        mon.is_monitoring = False
        return ok

    monkeypatch.setattr(mon, "update_auction_data", wrapped_update, raising=True)
    mon.update_interval = 0
    await mon.start_monitoring(dummy, realm="X")
    assert mon.last_update and 5 in mon.current_data

    await mon.stop_monitoring()
    assert mon.is_monitoring is False
