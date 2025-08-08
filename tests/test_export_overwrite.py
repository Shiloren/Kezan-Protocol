"""Pruebas para la exportación con sobrescritura."""

from kezan.export import export_data


def test_export_overwrite(tmp_path):
    """Comprueba que no se sobrescriba a menos que se indique."""

    file = tmp_path / "datos.json"
    file.write_text("[]")

    nuevo = export_data([{"a": 1}], str(file))
    assert nuevo != file

    sobre = export_data([{"a": 1}], str(file), overwrite=True)
    assert sobre == file

