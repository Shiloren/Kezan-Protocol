import types
import pytest


@pytest.mark.asyncio
async def test_get_top_items_success_and_cache(monkeypatch):
    # Import here to ensure monkeypatching works against module objects
    from kezan import analyzer
    from kezan import cache as kezan_cache

    # In-memory cache shim
    mem = {}

    def fake_get(key):
        return mem.get(key)

    def fake_set(key, value, ttl):
        mem[key] = value

    # Mock fetch_auction_data
    async def fake_fetch():
        return {
            "auctions": [
                {"item": {}, "buyout": 100, "quantity": 2},  # missing id -> warn/skip
                {"item": {"id": 101}, "buyout": 150, "quantity": 3},  # margin ~0.33 -> include
                {"item": {"id": 202}, "buyout": 100, "quantity": 1},  # margin ~0.33 -> include
                {"item": {"id": 303}, "buyout": 1000, "quantity": 1000},  # unit=1, avg=1.5, margin ~0.33 -> include
                {"item": {"id": 404}, "buyout": 100, "quantity": 100},  # unit=1, margin ~0.33 -> include
                {"item": {"id": 505}, "buyout": 1, "quantity": 1},  # unit=1, margin ~0.33 -> include
            ]
        }

    # Wire patches
    monkeypatch.setattr(kezan_cache, "get", fake_get)
    monkeypatch.setattr(kezan_cache, "set", fake_set)
    monkeypatch.setattr(analyzer, "fetch_auction_data", fake_fetch)

    # First call hits fetch and populates cache
    res1 = await analyzer.get_top_items(limit=2, min_margin=0.3)
    assert isinstance(res1, dict) and "items" in res1
    assert len(res1["items"]) == 2
    # Second call should be served from cache without invoking fetch again
    # Replace fetch with a sentinel to ensure it's not called
    async def sentinel_fetch():
        raise AssertionError("fetch_auction_data should not be called due to cache")

    monkeypatch.setattr(analyzer, "fetch_auction_data", sentinel_fetch)
    res2 = await analyzer.get_top_items(limit=2, min_margin=0.3)
    assert res2 == res1


@pytest.mark.asyncio
async def test_get_top_items_runtime_error(monkeypatch):
    from kezan import analyzer
    from kezan import cache as kezan_cache

    # Ensure cache miss
    monkeypatch.setattr(kezan_cache, "get", lambda k: None)
    monkeypatch.setattr(kezan_cache, "set", lambda k, v, ttl: None)

    async def boom():
        raise RuntimeError("API down")

    monkeypatch.setattr(analyzer, "fetch_auction_data", boom)
    res = await analyzer.get_top_items(limit=1, min_margin=0.5)
    assert res == {"error": "API down"}


@pytest.mark.asyncio
async def test_get_top_items_no_data(monkeypatch):
    from kezan import analyzer
    from kezan import cache as kezan_cache

    # Ensure cache miss
    monkeypatch.setattr(kezan_cache, "get", lambda k: None)
    monkeypatch.setattr(kezan_cache, "set", lambda k, v, ttl: None)

    async def no_data():
        return None

    monkeypatch.setattr(analyzer, "fetch_auction_data", no_data)
    res = await analyzer.get_top_items()
    assert res == {"error": "No se pudieron obtener los datos de subasta."}
