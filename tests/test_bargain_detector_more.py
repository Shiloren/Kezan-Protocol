from kezan.bargain_detector import Lot, Config, Stats, detect_bargains


class DummyHistory:
    def __init__(self, stats):
        self._stats = stats
    def get_stats(self, key):
        return self._stats


def test_detect_bargains_anomaly_boost_and_limits():
    stats = Stats(P50_7d=100, P50_30d=120, MAD_7d=10, vol_7d=500, rot=0.8)
    h = DummyHistory(stats)
    # Create a strong anomaly: price way below P50_7d to trigger z <= -2 boost
    lot = Lot(item_id=1, quantity=1, scope="eu", is_commodity=True, price_u=50)
    cfg = Config(bargain_score_min=0.5)
    out = detect_bargains([lot], h, capital=10000, cfg=cfg)
    assert out and out[0]["recommendation_type"] == "RECOMMEND_BUY" and out[0]["qty_sugerida"] > 0

    # Non-commodity liquidity threshold branch
    stats2 = Stats(P50_7d=100, P50_30d=100, MAD_7d=5, vol_7d=10, rot=0.2)
    h2 = DummyHistory(stats2)
    lot2 = Lot(item_id=2, quantity=1, scope="1080", is_commodity=False, price_u=50)
    out2 = detect_bargains([lot2], h2, capital=10000, cfg=cfg)
    # Not enough liquidity -> no recommendations
    assert out2 == []
