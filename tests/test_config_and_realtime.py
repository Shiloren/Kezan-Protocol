from datetime import datetime

from fastapi.testclient import TestClient

from kezan.ai_framework.config_manager import ConfigManager
from kezan.realtime_monitor import RealTimeAuctionMonitor, RealTimeAuctionData
from kezan import main as app_main


def test_config_manager_crud(tmp_path):
    cfg = ConfigManager(str(tmp_path / "cfg"))
    creds = cfg.get_api_credentials()
    assert "client_id" in creds and "client_secret" in creds

    cfg.update_api_credentials("X", "Y")
    assert cfg.get_api_credentials()["client_id"] == "X"

    cfg.update_preferences(default_realm="EU-Server", auto_analysis=False)
    prefs = cfg.get_preferences()
    assert prefs["default_realm"] == "EU-Server" and prefs["auto_analysis"] is False

    cfg.add_favorite_server("A")
    assert "A" in cfg.get_favorite_servers()
    cfg.remove_favorite_server("A")
    assert "A" not in cfg.get_favorite_servers()

    cfg.update_ai_settings(analysis_interval=120)
    assert cfg.get_ai_settings()["analysis_interval"] == 120


def test_realtime_monitor_basics():
    mon = RealTimeAuctionMonitor()
    # Pre-carga datos simulados sin tocar red
    now = datetime.now()
    mon.last_update = now
    mon.current_data[1] = [
        RealTimeAuctionData(timestamp=now, item_id=1, current_price=10, quantity=2, is_buyout=True, time_left="SHORT"),
        RealTimeAuctionData(timestamp=now, item_id=1, current_price=10, quantity=1, is_buyout=False, time_left="LONG"),
        RealTimeAuctionData(timestamp=now, item_id=1, current_price=12, quantity=5, is_buyout=True, time_left="MEDIUM"),
    ]
    price = mon.get_current_price(1)
    assert price and price["price"] == 10 and price["quantity"] == 3
    snap = mon.get_market_snapshot([1])
    assert 1 in snap and snap[1]["lowest_price"] == 10 and snap[1]["highest_price"] == 12


def test_main_root():
    client = TestClient(app_main.app)
    resp = client.get("/")
    assert resp.status_code == 200 and resp.json().get("message")
