import httpx
import os

from kezan.config import API_CLIENT_ID, API_CLIENT_SECRET, REGION, REALM_ID

BLIZZ_TOKEN_URL = f"https://{REGION}.battle.net/oauth/token"
BLIZZ_AUCTION_URL = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{REALM_ID}/auctions"
NAMESPACE = f"dynamic-{REGION}"


async def get_access_token():
    """Solicita un token OAuth2 de Blizzard (a implementar cuando se configuren las claves)."""
    if not API_CLIENT_ID or not API_CLIENT_SECRET:
        raise RuntimeError("Las claves de la API de Blizzard no están configuradas.")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            BLIZZ_TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(API_CLIENT_ID, API_CLIENT_SECRET),
        )
        response.raise_for_status()
        return response.json()["access_token"]


async def fetch_auction_data():
    """Obtiene los datos de subasta del reino (a implementar)."""
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": NAMESPACE, "locale": "en_US"}

    async with httpx.AsyncClient() as client:
        response = await client.get(BLIZZ_AUCTION_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
