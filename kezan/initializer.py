"""Inicializador interactivo para credenciales de la API de Blizzard.

Este módulo valida la presencia de credenciales y, si faltan, solicita al
usuario (por GUI o consola) que las ingrese y las guarda en ``.env`` para el
resto de la aplicación.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple
import os

import httpx
from dotenv import load_dotenv
from kezan.logger import get_logger

try:  # GUI imports (optional during unit tests)
    import tkinter as tk
    from tkinter import simpledialog
except Exception:  # pragma: no cover - Tkinter may be absent in tests
    tk = None  # type: ignore
    simpledialog = None  # type: ignore
    messagebox = None  # type: ignore

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
REQUIRED_VARS = ["BLIZZ_CLIENT_ID", "BLIZZ_CLIENT_SECRET", "REGION", "REALM_ID"]

logger = get_logger(__name__)


def _try_request_token(client_id: str, client_secret: str, region: str) -> Tuple[bool, str]:
    """Intenta obtener un token OAuth para validar credenciales.

    Retorna:
    - Tuple[bool, str]: ``(ok, error)`` donde ``ok`` indica éxito y ``error`` el
      mensaje asociado cuando falla.
    """
    token_url = f"https://{region}.battle.net/oauth/token"
    try:
        response = httpx.post(
            token_url,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=10,
        )
        response.raise_for_status()
        return True, ""
    except httpx.RequestError as exc:  # Network error
        return False, f"Network error: {exc}"
    except httpx.HTTPStatusError as exc:  # Invalid credentials
        return False, f"HTTP error: {exc.response.status_code}"  # pragma: no cover


def check_credentials_validity() -> bool:
    """Verifica si las variables de entorno actuales producen un token válido."""
    load_dotenv(override=True)
    client_id = os.getenv("BLIZZ_CLIENT_ID", "")
    client_secret = os.getenv("BLIZZ_CLIENT_SECRET", "")
    region = os.getenv("REGION", "")

    if not client_id or not client_secret or not region:
        return False

    ok, _ = _try_request_token(client_id, client_secret, region)
    return ok


def prompt_for_credentials_console() -> bool:
    """Solicita las credenciales de Blizzard por consola."""
    logger.warning("Credenciales de Blizzard no configuradas o inválidas.")
    client_id = input("BLIZZ_CLIENT_ID: ").strip()
    client_secret = input("BLIZZ_CLIENT_SECRET: ").strip()
    region = input("REGION (ej. eu): ").strip() or "eu"
    realm_id = input("REALM_ID (ej. 1080): ").strip() or "1080"

    ok, error = _try_request_token(client_id, client_secret, region)
    if not ok:
        logger.error("Error verificando credenciales: %s", error)
        return False

    save_env_file(
        {
            "BLIZZ_CLIENT_ID": client_id,
            "BLIZZ_CLIENT_SECRET": client_secret,
            "REGION": region,
            "REALM_ID": realm_id,
        }
    )
    logger.info("Credenciales guardadas en .env")
    load_dotenv(override=True)
    return True


def prompt_for_credentials_gui() -> bool:
    """Solicita las credenciales de Blizzard mediante diálogos Tkinter."""
    if tk is None or simpledialog is None:
        return prompt_for_credentials_console()

    root = tk.Tk()
    root.withdraw()
    while True:
        client_id = simpledialog.askstring("Blizzard API", "BLIZZ_CLIENT_ID:")
        if client_id is None:
            return False
        client_secret = simpledialog.askstring(
            "Blizzard API", "BLIZZ_CLIENT_SECRET:", show="*"
        )
        if client_secret is None:
            return False
        region = simpledialog.askstring("Blizzard API", "REGION (ej. eu):", initialvalue="eu")
        if region is None:
            return False
        realm_id = simpledialog.askstring(
            "Blizzard API", "REALM_ID (ej. 1080):", initialvalue="1080"
        )
        if realm_id is None:
            return False

        ok, error = _try_request_token(client_id, client_secret, region)
        if ok:
            save_env_file(
                {
                    "BLIZZ_CLIENT_ID": client_id,
                    "BLIZZ_CLIENT_SECRET": client_secret,
                    "REGION": region,
                    "REALM_ID": realm_id,
                }
            )
            logger.info("Credenciales guardadas correctamente")
            load_dotenv(override=True)
            return True
        if "Network error" in error:
            logger.error(error)
            return False
        logger.error("Credenciales inválidas, intenta de nuevo")


def save_env_file(data: Dict[str, str]) -> None:
    """Escribe las credenciales proporcionadas en el archivo ``.env``."""
    lines = [f"{key}={value}\n" for key, value in data.items()]
    ENV_PATH.write_text("".join(lines))


def ensure_credentials(use_gui: bool = False) -> bool:
    """Garantiza que existen credenciales válidas.

    Retorna ``True`` si las credenciales son válidas o se obtuvieron
    satisfactoriamente. Retorna ``False`` si el usuario cancela o hay error
    de conexión.
    """
    if check_credentials_validity():
        return True

    if use_gui:
        return prompt_for_credentials_gui()
    return prompt_for_credentials_console()
