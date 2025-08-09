from datetime import datetime

from kezan.realtime_monitor import RealTimeAuctionMonitor


def test_get_current_price_empty_and_none():
    mon = RealTimeAuctionMonitor()
    assert mon.get_current_price(9999) is None
    mon.current_data[1] = []
    assert mon.get_current_price(1) is None


def test_market_snapshot_missing_items():
    mon = RealTimeAuctionMonitor()
    now = datetime.now()
    mon.last_update = now
    # No data for item 3; only 1
    class _D:
        def __init__(self, price, qty):
            self.current_price = price
            self.quantity = qty
            self.time_left = "SHORT"
    mon.current_data[1] = [_D(1, 1), _D(2, 2)]
    snap = mon.get_market_snapshot([1, 3])
    assert 1 in snap and 3 not in snap
