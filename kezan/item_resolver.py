"""Resuelve nombres legibles de items usando la API de Blizzard."""
from __future__ import annotations

from typing import Dict

import httpx

from kezan.config import API_CLIENT_ID, API_CLIENT_SECRET, REGION

_TOKEN_URL = f"https://{REGION}.battle.net/oauth/token"
_ITEM_URL = f"https://{REGION}.api.blizzard.com/data/wow/item/{{item_id}}"
_NAMESPACE = f"static-{REGION}"

_token_cache: str | None = None
_name_cache: Dict[int, str] = {}


def _get_access_token() -> str:
    """Obtiene y cachea un token OAuth2 para la API de Blizzard."""
    global _token_cache
    if _token_cache:
        return _token_cache
    if not API_CLIENT_ID or not API_CLIENT_SECRET:
        raise RuntimeError("Las claves de la API de Blizzard no están configuradas.")
    resp = httpx.post(
        _TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(API_CLIENT_ID, API_CLIENT_SECRET),
        timeout=10,
    )
    resp.raise_for_status()
    _token_cache = resp.json().get("access_token", "")
    if not _token_cache:
        raise RuntimeError("No access token returned")
    return _token_cache


def resolve_item_name(item_id: int) -> str:
    """Devuelve el nombre legible del item indicado.

    Si la solicitud falla, se devuelve "ItemID xxxx" como alternativa.
    """
    if not item_id:
        return "ItemID unknown"
    if item_id in _name_cache:
        return _name_cache[item_id]
    try:
        token = _get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"namespace": _NAMESPACE, "locale": "en_US"}
        url = _ITEM_URL.format(item_id=item_id)
        resp = httpx.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        name = resp.json().get("name")
        if name:
            _name_cache[item_id] = name
            return name
    except Exception:
        pass
    return f"ItemID {item_id}"
