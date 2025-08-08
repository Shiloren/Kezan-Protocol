"""Pruebas adicionales para la exportación de datos."""

import pytest

from kezan.export import export_data


def test_export_csv_empty(tmp_path):
    """Exporta una lista vacía a CSV y valida el contenido."""
    destino = tmp_path / "vacio.csv"
    export_data([], str(destino))
    assert destino.read_text() == ""


def test_export_invalid_extension(tmp_path):
    """Comprueba que extensiones no soportadas generan error."""
    destino = tmp_path / "datos.txt"
    with pytest.raises(ValueError):
        export_data([], str(destino))
