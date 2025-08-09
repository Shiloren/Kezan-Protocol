import importlib

def test_has_blizzard_credentials_env(monkeypatch):
    # Set env before importing to ensure module constants pick them up
    monkeypatch.setenv("BLIZZ_CLIENT_ID", "id")
    monkeypatch.setenv("BLIZZ_CLIENT_SECRET", "secret")
    monkeypatch.setenv("REGION", "eu")
    import kezan.config as cfg
    importlib.reload(cfg)
    # call through reloaded module to ensure fresh constants
    assert cfg.has_blizzard_credentials() is True

from kezan.config import validate_local_model_path


def test_validate_local_model_path(tmp_path):
    # Non-existent dir returns False
    assert validate_local_model_path(str(tmp_path/"missing")) is False
    # Existing dir True
    assert validate_local_model_path(str(tmp_path)) is True
