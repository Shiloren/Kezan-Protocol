"""Pruebas para exportaciones con archivos bloqueados."""

import logging
from pathlib import Path

import pytest

from kezan import export


def test_export_data_locked_file(monkeypatch, caplog):
    """Lanza error y registra cuando el archivo está bloqueado."""

    def fake_write(self, *args, **kwargs):
        raise PermissionError("locked")

    monkeypatch.setattr(Path, "write_text", fake_write)
    caplog.set_level(logging.ERROR)
    with pytest.raises(PermissionError):
        export.export_data([{"a": 1}], "out.json")
    assert "No se pudo exportar" in caplog.text
