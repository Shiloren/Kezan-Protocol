"""Pruebas para la interacción con la API de Blizzard."""

import httpx
import pytest

from kezan import blizzard_api


class FakeResponse:
    """Respuesta simulada para llamadas HTTP."""

    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


@pytest.mark.asyncio
async def test_get_access_token_and_cache(monkeypatch):
    """Obtiene token y utiliza la caché."""
    monkeypatch.setattr(blizzard_api, "API_CLIENT_ID", "id")
    monkeypatch.setattr(blizzard_api, "API_CLIENT_SECRET", "sec")
    store = {}
    monkeypatch.setattr(blizzard_api.cache, "get", lambda k: store.get(k))
    monkeypatch.setattr(blizzard_api.cache, "set", lambda k, v, ttl: store.update({k: v}))

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, *a, **k):
            return FakeResponse({"access_token": "tok"})

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Client())
    tok1 = await blizzard_api.get_access_token()
    tok2 = await blizzard_api.get_access_token()
    assert tok1 == tok2 == "tok"


@pytest.mark.asyncio
async def test_get_access_token_errors(monkeypatch):
    """Cubre errores de red y de estado HTTP."""
    monkeypatch.setattr(blizzard_api, "API_CLIENT_ID", "id")
    monkeypatch.setattr(blizzard_api, "API_CLIENT_SECRET", "sec")
    monkeypatch.setattr(blizzard_api.cache, "get", lambda k: None)

    class ClientReqErr:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, *a, **k):
            raise httpx.RequestError("boom", request=None)

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: ClientReqErr())
    assert await blizzard_api.get_access_token() is None

    class ClientHttpErr:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, *a, **k):
            raise httpx.HTTPStatusError("boom", request=None, response=None)

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: ClientHttpErr())
    assert await blizzard_api.get_access_token() is None


@pytest.mark.asyncio
async def test_fetch_auction_data(monkeypatch):
    """Descarga datos de subasta utilizando token simulado."""
    monkeypatch.setattr(blizzard_api, "API_CLIENT_ID", "id")
    monkeypatch.setattr(blizzard_api, "API_CLIENT_SECRET", "sec")
    store = {}
    monkeypatch.setattr(blizzard_api.cache, "get", lambda k: store.get(k))
    monkeypatch.setattr(blizzard_api.cache, "set", lambda k, v, ttl: store.update({k: v}))

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, *a, **k):
            return FakeResponse({"access_token": "tok"})

        async def get(self, *a, **k):
            return FakeResponse({"auctions": []})

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Client())
    data = await blizzard_api.fetch_auction_data()
    assert data == {"auctions": []}


@pytest.mark.asyncio
async def test_fetch_auction_data_error(monkeypatch):
    """Propaga None ante errores y falta de token."""
    monkeypatch.setattr(blizzard_api, "API_CLIENT_ID", "id")
    monkeypatch.setattr(blizzard_api, "API_CLIENT_SECRET", "sec")
    monkeypatch.setattr(blizzard_api.cache, "get", lambda k: None)

    async def fake_get_access_token():
        return None

    monkeypatch.setattr(blizzard_api, "get_access_token", fake_get_access_token)
    assert await blizzard_api.fetch_auction_data() is None

    async def token_ok():
        return "tok"

    monkeypatch.setattr(blizzard_api, "get_access_token", token_ok)

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *a, **k):
            raise httpx.HTTPStatusError("boom", request=None, response=None)

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: Client())
    assert await blizzard_api.fetch_auction_data() is None


@pytest.mark.asyncio
async def test_get_access_token_missing_credentials(monkeypatch):
    """Falla cuando no hay credenciales configuradas."""
    monkeypatch.setattr(blizzard_api, "API_CLIENT_ID", "")
    monkeypatch.setattr(blizzard_api, "API_CLIENT_SECRET", "")
    with pytest.raises(RuntimeError):
        await blizzard_api.get_access_token()

