import asyncio
from datetime import datetime, timedelta

import pytest

from kezan.ai_framework.api_controller import AIAPIController


class DummyBlizzard:
    async def fetch_auction_data(self):
        return {"auctions": []}


@pytest.mark.asyncio
async def test_api_controller_rate_limit_and_analysis(monkeypatch, tmp_path):
    ctl = AIAPIController()
    # Aislar memoria en carpeta temporal
    from kezan.ai_framework.memory_manager import ContextMemory
    ctl.memory = ContextMemory(storage_path=str(tmp_path / "mem"))
    ctl.blizzard_api = DummyBlizzard()

    # Force limit to 0 to hit False path
    info = ctl.rate_limits["auction_house"]
    info["limit"] = 0
    assert await ctl.get_auction_data("x") is None

    # Analyze market data with patterns
    data = {
        1: [
            {"unit_price": 10, "quantity": 1},
            {"unit_price": 30, "quantity": 1},
        ],
        2: [
            {"unit_price": 5, "quantity": 1},
            {"unit_price": 6, "quantity": 1},
        ],
    }
    analysis = await ctl.analyze_market_data(data)
    assert 1 in analysis and 2 in analysis

    # Strategy selection uses memory patterns
    strat = ctl.get_optimal_strategy(1, current_price=9)
    assert strat["action"] in {"hold", "buy"}

    # Price range categories
    assert ctl._get_price_range(50) == "very_low"
    assert ctl._get_price_range(500) == "low"
    assert ctl._get_price_range(5000) == "medium"
    assert ctl._get_price_range(50000) == "high"
    assert ctl._get_price_range(500000) == "very_high"
