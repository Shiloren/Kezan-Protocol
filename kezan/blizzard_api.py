import httpx

from kezan.config import API_CLIENT_ID, API_CLIENT_SECRET, REGION, REALM_ID
from kezan.logger import get_logger
from kezan import cache

BLIZZ_TOKEN_URL = f"https://{REGION}.battle.net/oauth/token"
BLIZZ_AUCTION_URL = (
    f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{REALM_ID}/auctions"
)
NAMESPACE = f"dynamic-{REGION}"

logger = get_logger(__name__)


async def get_access_token():
    """Solicita un token OAuth2 de Blizzard (a implementar cuando se configuren las claves)."""
    if not API_CLIENT_ID or not API_CLIENT_SECRET:
        raise RuntimeError("Las claves de la API de Blizzard no están configuradas.")

    cached = cache.get("oauth_token")
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(
                BLIZZ_TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(API_CLIENT_ID, API_CLIENT_SECRET),
            )
            response.raise_for_status()
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("Error al contactar con la API de Blizzard: %s", exc)
            return None
        except httpx.HTTPStatusError as exc:
            logger.error("Respuesta inválida de la API de Blizzard: %s", exc)
            return None

    token = response.json().get("access_token")
    if token:
        cache.set("oauth_token", token, ttl=3600)
    return token


async def fetch_auction_data():
    """Obtiene los datos de subasta del reino (a implementar)."""
    cached = cache.get("auction_data")
    if cached:
        return cached

    token = await get_access_token()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": NAMESPACE, "locale": "en_US"}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                BLIZZ_AUCTION_URL, headers=headers, params=params
            )
            response.raise_for_status()
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("Error al contactar con la API de Blizzard: %s", exc)
            return None
        except httpx.HTTPStatusError as exc:
            logger.error("Respuesta inválida de la API de Blizzard: %s", exc)
            return None

    data = response.json()
    cache.set("auction_data", data, ttl=300)
    return data
