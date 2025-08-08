import asyncio
import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan import analyzer
def test_missing_item(monkeypatch):
    async def fake_fetch():
        return {"auctions": [{"buyout": 100, "quantity": 1}, {"item": {"id": 1}, "buyout": 100, "quantity": 1}]}

    monkeypatch.setattr(analyzer, "fetch_auction_data", fake_fetch)
    result = asyncio.run(analyzer.get_top_items(limit=5, min_margin=0))
    assert len(result["items"]) == 1
