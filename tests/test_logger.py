"""Pruebas para el módulo de logging."""

from kezan.logger import get_logger


def test_get_logger_reuses_handlers(tmp_path, monkeypatch):
    """La segunda llamada debe reutilizar el logger existente."""
    monkeypatch.setattr("kezan.logger.LOG_DIR", tmp_path)
    monkeypatch.setattr("kezan.logger.LOG_FILE", tmp_path / "kezan.log")
    log1 = get_logger("demo")
    log2 = get_logger("demo")
    assert log1 is log2
