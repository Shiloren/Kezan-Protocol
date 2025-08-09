import importlib
import os

def test_blizz_and_blizzard_prefix_support(monkeypatch):
    # Prefer BLIZZ_* but also support BLIZZARD_*
    monkeypatch.delenv("BLIZZ_CLIENT_ID", raising=False)
    monkeypatch.delenv("BLIZZ_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("BLIZZARD_CLIENT_ID", "IDX")
    monkeypatch.setenv("BLIZZARD_CLIENT_SECRET", "SECX")
    import kezan.config as cfg
    importlib.reload(cfg)
    assert cfg.API_CLIENT_ID == "IDX" and cfg.API_CLIENT_SECRET == "SECX"

    # When BLIZZ_* present, they take precedence
    monkeypatch.setenv("BLIZZ_CLIENT_ID", "IDY")
    monkeypatch.setenv("BLIZZ_CLIENT_SECRET", "SECY")
    importlib.reload(cfg)
    assert cfg.API_CLIENT_ID == "IDY" and cfg.API_CLIENT_SECRET == "SECY"
