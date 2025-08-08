"""Pruebas para la resolución de nombres de items."""

import httpx
import pytest

from kezan import item_resolver


class FakeResp:
    """Respuesta HTTP simulada."""

    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_get_access_token(monkeypatch):
    """Obtiene y cachea un token de acceso."""
    monkeypatch.setattr(item_resolver, "API_CLIENT_ID", "id")
    monkeypatch.setattr(item_resolver, "API_CLIENT_SECRET", "sec")
    monkeypatch.setattr(item_resolver, "_token_cache", None)

    def fake_post(*a, **k):
        return FakeResp({"access_token": "tok"})

    monkeypatch.setattr(httpx, "post", fake_post)
    assert item_resolver._get_access_token() == "tok"
    # Reutiliza caché
    assert item_resolver._get_access_token() == "tok"


def test_get_access_token_error(monkeypatch):
    """Falla cuando faltan credenciales."""
    monkeypatch.setattr(item_resolver, "API_CLIENT_ID", "")
    monkeypatch.setattr(item_resolver, "API_CLIENT_SECRET", "")
    monkeypatch.setattr(item_resolver, "_token_cache", None)
    with pytest.raises(RuntimeError):
        item_resolver._get_access_token()


def test_get_access_token_no_token(monkeypatch):
    """Error cuando la respuesta no contiene token."""
    monkeypatch.setattr(item_resolver, "API_CLIENT_ID", "id")
    monkeypatch.setattr(item_resolver, "API_CLIENT_SECRET", "sec")
    monkeypatch.setattr(item_resolver, "_token_cache", None)

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: Resp())
    with pytest.raises(RuntimeError):
        item_resolver._get_access_token()


def test_resolve_item_name(monkeypatch):
    """Resuelve el nombre del item y usa caché en llamadas sucesivas."""
    monkeypatch.setattr(item_resolver, "_name_cache", {})
    monkeypatch.setattr(item_resolver, "_get_access_token", lambda: "tok")

    def fake_get(*a, **k):
        return FakeResp({"name": "Poción"})

    monkeypatch.setattr(httpx, "get", fake_get)
    assert item_resolver.resolve_item_name(1) == "Poción"
    # Segunda llamada usa caché
    assert item_resolver.resolve_item_name(1) == "Poción"


def test_resolve_item_name_fallback(monkeypatch):
    """Devuelve identificador cuando ocurre un error."""
    monkeypatch.setattr(item_resolver, "_get_access_token", lambda: "tok")

    def fake_get(*a, **k):
        raise httpx.HTTPError("fail")

    monkeypatch.setattr(httpx, "get", fake_get)
    assert item_resolver.resolve_item_name(0) == "ItemID unknown"
    assert item_resolver.resolve_item_name(9999) == "ItemID 9999"
