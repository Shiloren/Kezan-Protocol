"""Pruebas para ausencia de credenciales de la API."""

from kezan import initializer


def test_check_credentials_missing(monkeypatch):
    """Retorna False cuando faltan variables de entorno."""
    for var in ["BLIZZ_CLIENT_ID", "BLIZZ_CLIENT_SECRET", "REGION"]:
        monkeypatch.delenv(var, raising=False)
    assert not initializer.check_credentials_validity()
