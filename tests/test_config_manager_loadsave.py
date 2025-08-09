from pathlib import Path

from kezan.ai_framework.config_manager import ConfigManager


def test_config_manager_load_and_save(tmp_path):
    cfgdir = tmp_path / "cfg"
    cm = ConfigManager(str(cfgdir))
    # Defaults populated from config
    creds = cm.get_api_credentials()
    assert "client_id" in creds and "client_secret" in creds
    # Persist a change and reload
    cm.update_preferences(default_realm="X")
    cm2 = ConfigManager(str(cfgdir))
    assert cm2.get_preferences()["default_realm"] == "X"
