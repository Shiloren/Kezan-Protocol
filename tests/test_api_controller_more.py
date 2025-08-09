import pytest

from kezan.ai_framework.api_controller import AIAPIController


@pytest.mark.asyncio
async def test_get_auction_data_rate_limit_and_failure(monkeypatch):
    ctl = AIAPIController()
    # Force limit to 0 so first check fails
    ctl.rate_limits['auction_house']['limit'] = 0
    assert await ctl.get_auction_data(realm="ignored") is None

    # Now allow 1 call but make API raise to hit failure recording path
    ctl.rate_limits['auction_house']['limit'] = 1

    class BadAPI:
        async def fetch_auction_data(self):
            raise RuntimeError("down")

    monkeypatch.setattr(ctl, "blizzard_api", BadAPI())
    assert await ctl.get_auction_data(realm="ignored") is None


@pytest.mark.asyncio
async def test_analyze_market_data_and_strategy_branches(monkeypatch, tmp_path):
    ctl = AIAPIController()
    # Aislar la memoria para no contaminar otros tests
    from kezan.ai_framework.memory_manager import ContextMemory
    ctl.memory = ContextMemory(storage_path=str(tmp_path / "mem"))

    # Data with high volatility for item 1 and stable for 2
    data = {
        1: [
            {"unit_price": 10, "quantity": 1},
            {"unit_price": 40, "quantity": 2},
        ],
        2: [
            {"unit_price": 20, "quantity": 1},
            {"unit_price": 22, "quantity": 1},
        ],
    }

    analysis = await ctl.analyze_market_data(data)
    assert 1 in analysis and 2 in analysis

    # Add a successful similar strategy in memory to override action
    ctl.memory.add_similar_strategy({
        'item_id': 1,
        'price_range': ctl._get_price_range(15),
        'action': 'sell',
        'success_rate': 0.9,
    })

    # High volatility path recommends buy if below avg
    strat1 = ctl.get_optimal_strategy(1, current_price=15)
    assert strat1['action'] in {'buy', 'sell'} and strat1['confidence'] > 0

    # Price range categories
    assert ctl._get_price_range(50) == 'very_low'
    assert ctl._get_price_range(500) == 'low'
    assert ctl._get_price_range(5000) == 'medium'
    assert ctl._get_price_range(50000) == 'high'
    assert ctl._get_price_range(500000) == 'very_high'
