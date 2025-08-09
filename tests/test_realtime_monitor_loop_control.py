import asyncio
import pytest

from kezan.realtime_monitor import RealTimeAuctionMonitor


@pytest.mark.asyncio
async def test_start_and_stop_monitoring(monkeypatch):
    mon = RealTimeAuctionMonitor()

    class DummyAPI:
        async def get_auctions(self, realm):
            return []

    # Speed up loop
    mon.update_interval = 0.01
    # Stop after one iteration
    async def stop_soon():
        await asyncio.sleep(0.02)
        await mon.stop_monitoring()

    task = asyncio.create_task(mon.start_monitoring(DummyAPI(), realm="r"))
    await stop_soon()
    await asyncio.wait_for(task, timeout=1.0)
    assert mon.is_monitoring is False
