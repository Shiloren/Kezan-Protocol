import asyncio
import httpx
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan import blizzard_api
def test_fetch_auction_timeout(monkeypatch):
    async def fake_token():
        return "token"

    monkeypatch.setattr(blizzard_api, "get_access_token", fake_token)

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, *args, **kwargs):
            raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=10: DummyClient())
    data = asyncio.run(blizzard_api.fetch_auction_data())
    assert data is None
