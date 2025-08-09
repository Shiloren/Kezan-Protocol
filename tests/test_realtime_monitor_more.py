import pytest
from types import SimpleNamespace

from kezan.realtime_monitor import RealTimeAuctionMonitor


@pytest.mark.asyncio
async def test_update_auction_data_and_snapshot(monkeypatch):
    mon = RealTimeAuctionMonitor()

    async def fake_get_auctions(realm):
        return [
            {"item": {"id": 1}, "unit_price": 5, "quantity": 2, "time_left": "SHORT"},
            {"item": {"id": 1}, "unit_price": 5, "quantity": 3, "time_left": "MEDIUM"},
            {"item": {"id": 2}, "unit_price": 7, "quantity": 1, "time_left": "LONG"},
        ]

    ok = await mon.update_auction_data(SimpleNamespace(get_auctions=fake_get_auctions), realm="r1")
    assert ok is True
    # Current price aggregates same lowest price quantities and carries first time_left
    cp = mon.get_current_price(1)
    assert cp["price"] == 5 and cp["quantity"] == 5 and cp["time_left"] in {"SHORT", "MEDIUM"}

    snap = mon.get_market_snapshot([1, 2])
    assert 1 in snap and 2 in snap
    assert snap[1]["lowest_price"] == 5 and snap[1]["highest_price"] == 5 and snap[1]["available_quantity"] == 5
    assert snap[2]["lowest_price"] == 7 and snap[2]["num_auctions"] == 1


@pytest.mark.asyncio
async def test_update_auction_data_error_path(caplog):
    mon = RealTimeAuctionMonitor()

    class BadAPI:
        async def get_auctions(self, realm):
            raise RuntimeError("boom")

    with caplog.at_level("ERROR"):
        ok = await mon.update_auction_data(BadAPI(), realm="r1")
        assert ok is False
        assert any("Error actualizando datos" in rec.message for rec in caplog.records)
