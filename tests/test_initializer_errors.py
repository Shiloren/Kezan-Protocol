"""Pruebas para errores en la inicialización de credenciales."""

import httpx
from kezan import initializer


def test_try_request_token_invalid(monkeypatch):
    """Simula credenciales inválidas y verifica el mensaje de error."""

    def fake_post(*args, **kwargs):
        request = httpx.Request("POST", "url")
        response = httpx.Response(401, request=request)
        raise httpx.HTTPStatusError("unauthorized", request=request, response=response)

    monkeypatch.setattr(httpx, "post", fake_post)
    ok, error = initializer._try_request_token("id", "sec", "eu")
    assert not ok and "HTTP error" in error

