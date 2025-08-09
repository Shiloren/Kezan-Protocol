import sys
import types
import math
import pytest


class _Arr:
    def __init__(self, data):
        self.data = list(data)
    def __iter__(self):
        return iter(self.data)
    def __getitem__(self, idx):
        return self.data[idx]
    def __sub__(self, other):
        return _Arr([x - other for x in self.data])
    def __truediv__(self, other):
        return _Arr([x / other for x in self.data])
    def __gt__(self, other):
        return [x > other for x in self.data]


class DummyNumpy(types.SimpleNamespace):
    def array(self, x):
        return _Arr(x)
    def min(self, arr):
        data = arr.data if hasattr(arr, 'data') else list(arr)
        return min(data)
    def max(self, arr):
        data = arr.data if hasattr(arr, 'data') else list(arr)
        return max(data)
    def mean(self, arr):
        data = arr.data if hasattr(arr, 'data') else list(arr)
        return sum(data) / len(data)
    def median(self, arr):
        data = sorted(arr.data if hasattr(arr, 'data') else list(arr))
        n = len(data)
        mid = n // 2
        return data[mid] if n % 2 == 1 else (data[mid - 1] + data[mid]) / 2
    def std(self, arr):
        data = arr.data if hasattr(arr, 'data') else list(arr)
        m = self.mean(data)
        var = sum((x - m) ** 2 for x in data) / len(data)
        return math.sqrt(var) if var > 0 else 1.0
    def abs(self, arr):
        if isinstance(arr, list):
            return _Arr([abs(x) for x in arr])
        data = arr.data if hasattr(arr, 'data') else list(arr)
        return _Arr([abs(x) for x in data])
    def where(self, cond):
        # cond is list of booleans; return tuple with indices list
        seq = cond.data if hasattr(cond, 'data') else list(cond)
        idx = [i for i, v in enumerate(seq) if v]
        return (idx,)


@pytest.fixture(autouse=True)
def mock_numpy_module(monkeypatch):
    # Ensure a fresh dummy numpy is available for each test and cleaned up after
    # Also clear any previously imported market_optimizer to avoid leaked np patches
    monkeypatch.delitem(sys.modules, 'kezan.market_optimizer', raising=False)
    monkeypatch.setitem(sys.modules, 'numpy', DummyNumpy())
    yield
    monkeypatch.delitem(sys.modules, 'numpy', raising=False)
    # Also drop market_optimizer so other tests can re-import with their own shims
    monkeypatch.delitem(sys.modules, 'kezan.market_optimizer', raising=False)


def test_market_optimizer_with_mocked_numpy(tmp_path):
    from kezan.market_optimizer import MarketDataProcessor, LLMOptimizer, FallbackStrategy

    mdp = MarketDataProcessor(cache_dir=str(tmp_path / '.cache'))
    # Build 11 normal prices and 1 extreme to yield z-score > 3
    raw = []
    for _ in range(11):
        raw.append({"item": {"id": 1}, "unit_price": 10, "quantity": 1})
    raw.append({"item": {"id": 1}, "unit_price": 1000, "quantity": 1})
    # Add a second item for diversity
    raw.extend([
        {"item": {"id": 2}, "unit_price": 8, "quantity": 3},
        {"item": {"id": 2}, "unit_price": 9, "quantity": 2},
    ])

    processed = mdp.preprocess_auction_data(raw)
    assert processed and 1 in processed['summary'] and 2 in processed['summary']
    assert processed['summary'][1]['total_listings'] == 12
    # Expect at least one anomaly for item 1
    assert any(a['item_id'] == 1 for a in processed['anomalies'])

    mdp.cache_results('tkey', processed, ttl_minutes=1)
    cached = mdp.get_cached_results('tkey')
    assert cached and 'summary' in cached

    opt = LLMOptimizer(max_tokens_per_request=50)
    chunks = opt.chunk_market_data(processed)
    assert chunks and all('items' in c for c in chunks)
    _ = opt.optimize_prompt('{"item_id": 1}', {})
    opt.update_context_memory('1', {"ok": True})

    fb = FallbackStrategy()
    basic = fb.get_fallback_analysis(processed)
    assert 'basic_stats' in basic and 'simple_recommendations' in basic
