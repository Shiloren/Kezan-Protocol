"""Pruebas para la expiración de la caché."""

import time

from kezan import cache


def test_cache_expira_y_elimina(tmp_path, monkeypatch):
    """Verifica que las entradas expiran y se borran del disco."""
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cache, "CACHE_FILE", tmp_path / "cache.db")

    cache.set("x", "y", ttl=1)
    assert cache.get("x") == "y"

    ahora = time.time() + 2
    monkeypatch.setattr(cache.time, "time", lambda: ahora)
    assert cache.get("x") is None
    with cache._open_db() as db:
        assert "x" not in db
