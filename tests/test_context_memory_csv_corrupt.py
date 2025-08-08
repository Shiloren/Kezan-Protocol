"""Pruebas para CSVs mal formateados en context_memory."""

import logging

from kezan import context_memory


def test_load_context_from_csv_corrupt(tmp_path, caplog):
    """Ignora archivo CSV corrupto y registra error."""
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text('timestamp\n"sin_cerrar')
    caplog.set_level(logging.ERROR)
    context_memory.load_context_from_csv(str(bad_csv))
    assert "Error leyendo CSV" in caplog.text
