import httpx

from kezan.config import API_CLIENT_ID, API_CLIENT_SECRET, REGION, REALM_ID

# Define token and auction URLs based on region and realm
BLIZZ_TOKEN_URL = f"https://{REGION}.battle.net/oauth/token"
BLIZZ_AUCTION_URL = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{REALM_ID}/auctions"
# Namespace is required by the Blizzard API to scope data
NAMESPACE = f"dynamic-{REGION}"

async def get_access_token():
    """
    Request an OAuth access token from Blizzard.

    Raises:
        RuntimeError: If API credentials are not configured.
        httpx.HTTPStatusError: If the HTTP request fails.

    Returns:
        str: The access token string.
    """
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
    """
    Fetch the auction house data for the configured connected realm.

    Raises:
        RuntimeError: If API credentials are not configured.
        httpx.HTTPStatusError: If the HTTP request fails.

    Returns:
        dict: Parsed JSON data containing auction information.
    """
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": NAMESPACE, "locale": "en_US"}

    async with httpx.AsyncClient() as client:
        response = await client.get(BLIZZ_AUCTION_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()