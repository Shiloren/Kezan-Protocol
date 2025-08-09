from kezan.bargain_detector import (
    Lot,
    Stats,
    Config,
    detect_bargains,
    normalize_commodity_lot,
    normalize_noncommodity_lot,
)


class DummyHistory:
    def __init__(self, stats_map):
        self.stats_map = stats_map

    def get_stats(self, key):
        # key: (scope, item_id, quality)
        return self.stats_map.get(key)


def test_normalize_lots():
    c = normalize_commodity_lot("EU", {"item": {"id": 1}, "quantity": 5, "unit_price": 100})
    assert c.price_u == 100
    n = normalize_noncommodity_lot(44, {"item": {"id": 2}, "quantity": 2, "buyout": 1000})
    assert n and abs(n.price_u - 500.0) < 1e-6
    assert normalize_noncommodity_lot(44, {"item": {"id": 2}, "quantity": 2}) is None


def test_detect_bargains_rules_and_filters():
    # Prepare snapshot and history
    lot = Lot(item_id=100, quantity=10, scope="EU", is_commodity=True, price_u=70.0)
    stats = Stats(P50_7d=100.0, P50_30d=120.0, MAD_7d=10.0, vol_7d=500, rot=0.8)
    hist = DummyHistory({("EU", 100, None): stats})
    cfg = Config()

    recs = detect_bargains([lot], hist, capital=10000.0, cfg=cfg)
    assert len(recs) == 1
    r = recs[0]
    assert r["recommendation_type"] == "RECOMMEND_BUY"
    assert r["qty_sugerida"] > 0
    assert r["bargain_score"] >= cfg.bargain_score_min


def test_zscore_with_small_mad():
    lot = Lot(item_id=200, quantity=1, scope="EU", is_commodity=True, price_u=50.0)
    stats = Stats(P50_7d=100.0, P50_30d=100.0, MAD_7d=0.0, vol_7d=1000, rot=1.2)
    hist = DummyHistory({("EU", 200, None): stats})
    cfg = Config()

    recs = detect_bargains([lot], hist, capital=1000.0, cfg=cfg)
    assert recs  # candidate by anomaly
