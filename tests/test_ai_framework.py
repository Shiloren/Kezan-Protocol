import pytest

from kezan.ai_framework.api_controller import AIAPIController
from kezan.ai_framework.memory_manager import ContextMemory


@pytest.mark.asyncio
async def test_api_controller_rate_limit_and_analysis(monkeypatch):
    ctrl = AIAPIController()
    # Force low limit
    info = ctrl.rate_limits['auction_house']
    info['limit'] = 1

    # Mock BlizzardAPI call to avoid network
    async def fake_fetch():
        return {1: [{"unit_price": 10, "quantity": 2}, {"unit_price": 20, "quantity": 1}]}

    monkeypatch.setattr(ctrl.blizzard_api, "fetch_auction_data", fake_fetch)

    first = await ctrl.get_auction_data("EU")
    assert isinstance(first, dict)

    # Second should be limited
    second = await ctrl.get_auction_data("EU")
    assert second is None

    # Analyze market and ensure patterns can be added
    analysis = await ctrl.analyze_market_data({1: [{"unit_price": 10, "quantity": 1}, {"unit_price": 50, "quantity": 1}]})
    assert 1 in analysis and analysis[1]['min_price'] == 10

    # Strategy selection with no memory should default to hold/buy
    strat = ctrl.get_optimal_strategy(999, 5)
    assert strat['action'] in ("hold", "buy")


def test_memory_manager_persistence(tmp_path):
    store = tmp_path / "mem"
    mem = ContextMemory(str(store))
    mem.add_market_pattern(1, {"type": "high_volatility", "spread": 10, "avg_price": 20})
    pat = mem.get_market_patterns(1)
    assert pat and pat[0]['type'] == 'high_volatility'

    mem.add_successful_strategy({"item_id": 1, "price_range": "low", "action": "buy", "success_rate": 0.8})
    similar = mem.get_similar_strategies({"item_id": 1, "price_range": "low"})
    assert similar and similar[0]['action'] == 'buy'

    mem.record_api_interaction("auction_house", success=True, response_time=0.1)
    perf = mem.get_api_performance("auction_house")
    assert perf and perf['success_count'] >= 1
