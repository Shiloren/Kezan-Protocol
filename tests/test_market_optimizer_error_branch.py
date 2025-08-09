import sys
import types


def test_preprocess_error_branch(monkeypatch):
    # Provide a dummy numpy to allow module import
    class DummyNP(types.SimpleNamespace):
        def array(self, x):
            raise RuntimeError("boom")
    monkeypatch.setitem(sys.modules, "numpy", DummyNP())

    try:
        from kezan.market_optimizer import MarketDataProcessor

        mdp = MarketDataProcessor()
        # Monkeypatch the imported numpy symbol to our failing one
        class BadNP(types.SimpleNamespace):
            def array(self, x):
                raise RuntimeError("boom")
        monkeypatch.setattr("kezan.market_optimizer.np", BadNP())
        out = mdp.preprocess_auction_data([{"item": {"id": 1}, "unit_price": 1}])
        assert out is None
    finally:
        # Ensure later tests can import with their own numpy shim
        monkeypatch.delitem(sys.modules, "kezan.market_optimizer", raising=False)
        monkeypatch.delitem(sys.modules, "numpy", raising=False)
