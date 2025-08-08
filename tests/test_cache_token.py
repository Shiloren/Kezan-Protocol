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
def test_token_cached(monkeypatch):
    monkeypatch.setattr(blizzard_api, "API_CLIENT_ID", "id")
    monkeypatch.setattr(blizzard_api, "API_CLIENT_SECRET", "secret")
    monkeypatch.setattr(blizzard_api, "REGION", "eu")

    class DummyClient:
        def __init__(self):
            self.post_calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, *args, **kwargs):
            self.post_calls += 1

            class Resp:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {"access_token": "token"}

            return Resp()

    dummy = DummyClient()
    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=10: dummy)

    t1 = asyncio.run(blizzard_api.get_access_token())
    t2 = asyncio.run(blizzard_api.get_access_token())
    assert t1 == "token"
    assert t2 == "token"
    assert dummy.post_calls == 1
