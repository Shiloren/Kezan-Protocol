import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest

from kezan.ai_controller import AIController, AIControllerConfig
from kezan.realtime_monitor import RealTimeAuctionMonitor
from kezan.realtime_monitor import RealTimeAuctionData, RealTimeMarketAnalyzer
from kezan.auction_analyzer import AuctionAnalyzer
from kezan.profile_manager import GameVersion, ProfileManager
import importlib.util


class DummyBlizzard:
    async def fetch_auction_data(self):
        return {"ok": True}

    async def get_auctions(self, realm: str):
        # Minimal synthetic auctions
        return [
            {"item": {"id": 1}, "unit_price": 10, "quantity": 2, "buyout": 100, "time_left": "SHORT"},
            {"item": {"id": 1}, "unit_price": 12, "quantity": 1, "buyout": 0, "time_left": "LONG"},
            {"item": {"id": 2}, "unit_price": 8, "quantity": 3, "buyout": 80, "time_left": "MEDIUM"},
        ]


class DummyLLM:
    async def analyze_intent(self, query: str):
        if "api" in query:
            return {"type": "test", "operation": "fetch", "requires_api_call": True, "requires_file_access": False}
        if "file" in query:
            # use a path inside repo to pass validation
            return {"type": "test", "operation": "read", "requires_api_call": False, "requires_file_access": True, "file_path": __file__}
        return {"type": "test", "operation": "noop", "requires_api_call": False, "requires_file_access": False}

    async def analyze_market_opportunity(self, *args, **kwargs):
        return {"analysis": "ok", "opportunity": False, "reason": "test"}

    async def scan_auction_house(self, *args, **kwargs):
        return []

    def suggest_search_strategy(self, *args, **kwargs):
        return "Estrategia breve"


@pytest.mark.asyncio
async def test_ai_controller_process_request_branches(tmp_path, monkeypatch):
    cfg = AIControllerConfig(max_requests_per_minute=5, memory_file=str(tmp_path / "mem.json"))
    ctl = AIController(cfg)
    # Inject dummies
    ctl.blizzard_api = DummyBlizzard()
    ctl.llm = DummyLLM()

    # API branch
    res_api = await ctl.process_request("please call api")
    assert res_api.get("ok") is True

    # File branch
    res_file = await ctl.process_request("do file read")
    # _read_file returns dict-like; here we expect either content or error structure
    assert isinstance(res_file, dict)

    # Local/noop branch
    res_local = await ctl.process_request("just chat")
    assert res_local.get("status") == "ok" and res_local.get("operation") == "noop"


@pytest.mark.asyncio
async def test_realtime_monitor_update(monkeypatch):
    mon = RealTimeAuctionMonitor()
    dummy = DummyBlizzard()
    ok = await mon.update_auction_data(dummy, realm="X")
    assert ok is True and mon.last_update and mon.current_data
    cur = mon.get_current_price(1)
    assert cur and cur["price"] == 10 and cur["quantity"] == 2


@pytest.mark.asyncio
async def test_auction_analyzer_methods(tmp_path, monkeypatch):
    # Ensure profile has an item to watch and a threshold
    pm = ProfileManager(config_dir=str(tmp_path / "profiles"))
    pm.update_preferences(GameVersion.RETAIL, default_realm="Realm")
    pm.add_watched_item(GameVersion.RETAIL, 1, max_price=11)

    az = AuctionAnalyzer()
    # Inject profile manager to use our temp dir
    az.profile_manager = pm
    # Inject dummies for network/LLM
    az.blizzard_api = DummyBlizzard()
    az.llm = DummyLLM()

    # Real-time off to hit non-realtime path deterministically
    res = await az.analyze_watched_items(GameVersion.RETAIL, realm="Realm", use_realtime=False)
    assert isinstance(res, list)

    insights = await az.get_market_insights(GameVersion.RETAIL, realm="Realm")
    assert "strategy" in insights and "market_trends" in insights

    alerts = await az.monitor_price_thresholds(GameVersion.RETAIL, realm="Realm")
    # threshold 11 vs min price 10 => one alert expected for item 1
    assert any(a["item_id"] == 1 for a in alerts)


def test_market_optimizer_components(tmp_path):
    # Skip if numpy not installed to avoid import errors from market_optimizer
    if importlib.util.find_spec("numpy") is None:
        pytest.skip("numpy not installed; skipping market_optimizer tests")

    from kezan.market_optimizer import MarketDataProcessor, LLMOptimizer, FallbackStrategy

    mdp = MarketDataProcessor(cache_dir=str(tmp_path / ".cache"))
    raw = [
        {"item": {"id": 1}, "unit_price": 10, "quantity": 2},
        {"item": {"id": 1}, "unit_price": 12, "quantity": 1},
        {"item": {"id": 2}, "unit_price": 8, "quantity": 3},
    ]
    proc = mdp.preprocess_auction_data(raw)
    assert proc and 1 in proc["summary"] and 2 in proc["summary"]
    mdp.cache_results("k", proc, ttl_minutes=1)
    cached = mdp.get_cached_results("k")
    assert cached and cached["summary"]

    # LLMOptimizer chunking and prompt
    opt = LLMOptimizer(max_tokens_per_request=20)
    chunks = opt.chunk_market_data(proc)
    assert chunks and all("items" in c for c in chunks)
    prompt = opt.optimize_prompt("{\"item_id\": 1}", {})
    assert "Analiza" in prompt and "Datos actuales" in prompt

    # FallbackStrategy
    fb = FallbackStrategy()
    analysis = fb.get_fallback_analysis(proc)
    assert analysis and "basic_stats" in analysis


@pytest.mark.asyncio
async def test_realtime_market_analyzer_item():
    now = datetime.now()
    mon = RealTimeAuctionMonitor()
    mon.last_update = now
    mon.current_data[1] = [
        RealTimeAuctionData(timestamp=now, item_id=1, current_price=10, quantity=2, is_buyout=True, time_left="SHORT")
    ]
    analyzer = RealTimeMarketAnalyzer(mon)

    class _LLM:
        async def analyze_market_opportunity(self, prompt):
            return {"analysis": "ok", "opportunity": False, "reason": "test"}

    res = await analyzer.analyze_item(1, historical_data=[{"p": 10}], llm_interface=_LLM())
    assert res["analysis"] and res["data_freshness"] in {"real_time", "stale"}


@pytest.mark.asyncio
async def test_ai_controller_permission_and_rate_limit(tmp_path):
    # Permission denied (operation not in allowlist)
    cfg = AIControllerConfig(allowed_operations=["read"], memory_file=str(tmp_path/"m.json"))
    ctl = AIController(cfg)
    ctl.llm = DummyLLM()
    res = await ctl.process_request("please call api")
    assert "Operación no permitida" in res.get("error", "")

    # Rate limit reached path
    cfg2 = AIControllerConfig(max_requests_per_minute=0, memory_file=str(tmp_path/"m2.json"))
    ctl2 = AIController(cfg2)
    ctl2.llm = DummyLLM()
    ctl2.blizzard_api = DummyBlizzard()
    res2 = await ctl2.process_request("please call api")
    assert res2.get("status") == "failed" and "Límite" in res2.get("error", "")


@pytest.mark.asyncio
async def test_auction_analyzer_realtime_branch(tmp_path):
    pm = ProfileManager(config_dir=str(tmp_path / "profiles"))
    pm.add_watched_item(GameVersion.RETAIL, 1, max_price=11)

    az = AuctionAnalyzer()
    az.profile_manager = pm
    az.blizzard_api = DummyBlizzard()
    az.llm = DummyLLM()

    # Pre-populate realtime data and mark monitoring active to skip starting background task
    now = datetime.now()
    az.realtime_monitor.last_update = now
    az.realtime_monitor.is_monitoring = True
    az.realtime_monitor.current_data[1] = [
        RealTimeAuctionData(timestamp=now, item_id=1, current_price=10, quantity=2, is_buyout=True, time_left="SHORT")
    ]
    res = await az.analyze_watched_items(GameVersion.RETAIL, realm="Realm", use_realtime=True)
    assert res and res[0]["item_id"] == 1
