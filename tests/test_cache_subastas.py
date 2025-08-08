import asyncio
import httpx
import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan import cache
from kezan import blizzard_api


@pytest.fixture(autouse=True)
def _clear_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(cache, "_cache_memory", {})
    monkeypatch.setattr(cache, "CACHE_FILE", tmp_path / "cache.db")
    yield
def test_auction_cache(monkeypatch):
    async def fake_token():
        return "token"

    monkeypatch.setattr(blizzard_api, "get_access_token", fake_token)
    monkeypatch.setattr(blizzard_api, "REGION", "eu")

    class DummyClient:
        def __init__(self):
            self.get_calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, *args, **kwargs):
            self.get_calls += 1

            class Resp:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {"auctions": []}

            return Resp()

    dummy = DummyClient()
    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=10: dummy)

    d1 = asyncio.run(blizzard_api.fetch_auction_data())
    d2 = asyncio.run(blizzard_api.fetch_auction_data())
    assert d1 == {"auctions": []}
    assert d2 == {"auctions": []}
    assert dummy.get_calls == 1
