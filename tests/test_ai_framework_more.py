import pytest

from kezan.ai_framework.api_controller import AIAPIController


def test__get_price_range_boundaries():
    ctrl = AIAPIController()
    # Boundary checks
    assert ctrl._get_price_range(0) == "very_low"
    assert ctrl._get_price_range(99) == "very_low"
    assert ctrl._get_price_range(100) == "low"
    assert ctrl._get_price_range(999) == "low"
    assert ctrl._get_price_range(1000) == "medium"
    assert ctrl._get_price_range(9999) == "medium"
    assert ctrl._get_price_range(10000) == "high"
    assert ctrl._get_price_range(99999) == "high"
    assert ctrl._get_price_range(100000) == "very_high"


@pytest.mark.asyncio
async def test_strategy_influence_by_memory(tmp_path):
    ctrl = AIAPIController()
    # Seed memory with successful strategy
    ctrl.memory.storage_path = tmp_path
    ctrl.memory.current_context = {}
    ctrl.memory.add_successful_strategy({
        "item_id": 1,
        "price_range": ctrl._get_price_range(50),
        "action": "buy",
        "success_rate": 0.9,
    })
    # Strategy should pick from memory
    s = ctrl.get_optimal_strategy(1, 50)
    assert s["action"] == "buy" and s["confidence"] >= 0.9
