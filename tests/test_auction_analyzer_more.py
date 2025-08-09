import asyncio
import pytest

from types import SimpleNamespace


@pytest.mark.asyncio
async def test_analyze_watched_items_realtime_and_non_realtime(monkeypatch):
    from kezan.auction_analyzer import AuctionAnalyzer
    from kezan.profile_manager import GameVersion

    aa = AuctionAnalyzer()

    # Fake profile with watched items and history
    class Prefs:
        watched_items = [1, 2]
        price_thresholds = {}

    fake_profile = SimpleNamespace(preferences=Prefs(), auction_history={1: [10, 12, 11]})

    # Patch profile manager
    monkeypatch.setattr(aa, "profile_manager", SimpleNamespace(get_profile=lambda gv: fake_profile))

    # Patch realtime monitor to trigger start_monitoring and return data for one item
    created_tasks = []

    def fake_create_task(coro):
        created_tasks.append("started")
        class _T: ...
        return _T()

    monkeypatch.setattr(asyncio, "create_task", fake_create_task)

    class FakeRTM:
        def __init__(self):
            self.is_monitoring = False
        async def start_monitoring(self, blizz, realm):
            self.is_monitoring = True
        def get_current_price(self, item_id):
            if item_id == 1:
                return {"item": {"id": 1}, "unit_price": 10, "quantity": 1}
            return None

    aa.realtime_monitor = FakeRTM()

    # Stub LLM to avoid network
    async def fake_analyze_market_opportunity(item_data, historical_prices):
        return {"signal": "hold", "score": 0.5}

    aa.llm = SimpleNamespace(
        analyze_market_opportunity=fake_analyze_market_opportunity,
        scan_auction_house=None,
        suggest_search_strategy=None,
    )

    # Stub BlizzardAPI; not used in realtime path besides start_monitoring
    aa.blizzard_api = SimpleNamespace(get_auctions=None)

    res_rt = await aa.analyze_watched_items(GameVersion.RETAIL, realm="realm-1", use_realtime=True)
    assert len(res_rt) == 1 and res_rt[0]["item_id"] == 1
    assert created_tasks, "start_monitoring should be scheduled when not monitoring"

    # Now test non-realtime path for item 2
    async def fake_get_auctions(realm):
        return [
            {"item": {"id": 2}, "unit_price": 9, "quantity": 2},
            {"item": {"id": 3}, "unit_price": 99, "quantity": 1},
        ]

    aa.blizzard_api = SimpleNamespace(get_auctions=fake_get_auctions)

    res_non = await aa.analyze_watched_items(GameVersion.RETAIL, realm="realm-1", use_realtime=False)
    assert len(res_non) == 1 and res_non[0]["item_id"] == 2


@pytest.mark.asyncio
async def test_get_market_insights_and_thresholds(monkeypatch):
    from kezan.auction_analyzer import AuctionAnalyzer
    from kezan.profile_manager import GameVersion

    aa = AuctionAnalyzer()

    # Build history > 10 entries to test slicing
    history = [{"price": p, "timestamp": f"t{p}"} for p in range(20)]

    class Prefs:
        watched_items = [10]
        price_thresholds = {1: 50, 2: 5}

    fake_profile = SimpleNamespace(preferences=Prefs(), auction_history={10: history})

    # Patch profile manager
    monkeypatch.setattr(aa, "profile_manager", SimpleNamespace(get_profile=lambda gv: fake_profile))

    # Patch LLM suggest strategy (sync function in current impl)
    aa.llm = SimpleNamespace(
        suggest_search_strategy=lambda item_history, market_trends, game_version: "focus-high-volume"
    )

    insights = await aa.get_market_insights(GameVersion.RETAIL, realm="ignored")
    assert insights["strategy"] == "focus-high-volume"
    assert insights["market_trends"] and len(insights["market_trends"][0]["price_history"]) == 10

    # Patch Blizzard auctions and test thresholds
    async def fake_get_auctions(realm):
        return [
            {"item": {"id": 1}, "unit_price": 40, "quantity": 1},
            {"item": {"id": 1}, "unit_price": 60, "quantity": 1},
            {"item": {"id": 2}, "unit_price": 10, "quantity": 1},
        ]

    aa.blizzard_api = SimpleNamespace(get_auctions=fake_get_auctions)

    alerts = await aa.monitor_price_thresholds(GameVersion.RETAIL, realm="r-1")
    assert len(alerts) == 1 and alerts[0]["item_id"] == 1 and alerts[0]["current_price"] == 40
