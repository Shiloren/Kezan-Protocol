"""Pruebas para la estructura del changelog."""

from kezan.changelog import log_change


def test_log_change_creates_entry(tmp_path, monkeypatch):
    """Verifica que la entrada siga el formato esperado."""

    monkeypatch.chdir(tmp_path)
    log_change("Entrada de prueba", "1.0.0")
    contenido = (tmp_path / "CHANGELOG.md").read_text().splitlines()
    assert contenido[0].startswith("## 1.0.0 -")
    assert contenido[1] == "Entrada de prueba"

