from __future__ import annotations

"""Interactive initializer for Blizzard API credentials.

This module provides helper functions to verify whether the Blizzard API
credentials are present and valid.  If not, it can prompt the user (via
GUI dialogs or console input) to provide the necessary information and
store it in a local ``.env`` file so that the rest of the application can
load it using :mod:`python-dotenv`.
"""

from pathlib import Path
from typing import Dict, Tuple
import os

import httpx
from dotenv import load_dotenv

try:  # GUI imports (optional during unit tests)
    import tkinter as tk
    from tkinter import simpledialog, messagebox
except Exception:  # pragma: no cover - Tkinter may be absent in tests
    tk = None  # type: ignore
    simpledialog = None  # type: ignore
    messagebox = None  # type: ignore

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
REQUIRED_VARS = ["BLIZZ_CLIENT_ID", "BLIZZ_CLIENT_SECRET", "REGION", "REALM_ID"]


def _try_request_token(client_id: str, client_secret: str, region: str) -> Tuple[bool, str]:
    """Attempt to obtain an OAuth token to validate credentials.

    Returns a tuple ``(ok, error)`` where ``ok`` indicates success.
    ``error`` contains an error message when ``ok`` is ``False``.
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
    """Check whether the current environment variables yield a valid token."""
    load_dotenv(override=True)
    client_id = os.getenv("BLIZZ_CLIENT_ID", "")
    client_secret = os.getenv("BLIZZ_CLIENT_SECRET", "")
    region = os.getenv("REGION", "")

    if not client_id or not client_secret or not region:
        return False

    ok, _ = _try_request_token(client_id, client_secret, region)
    return ok


def prompt_for_credentials_console() -> bool:
    """Prompt the user in the console for Blizzard credentials."""
    print("⚠️  Credenciales de Blizzard no configuradas o inválidas.")
    client_id = input("BLIZZ_CLIENT_ID: ").strip()
    client_secret = input("BLIZZ_CLIENT_SECRET: ").strip()
    region = input("REGION (ej. eu): ").strip() or "eu"
    realm_id = input("REALM_ID (ej. 1080): ").strip() or "1080"

    ok, error = _try_request_token(client_id, client_secret, region)
    if not ok:
        print(f"Error verificando credenciales: {error}")
        return False

    save_env_file(
        {
            "BLIZZ_CLIENT_ID": client_id,
            "BLIZZ_CLIENT_SECRET": client_secret,
            "REGION": region,
            "REALM_ID": realm_id,
        }
    )
    print("✅ Credenciales guardadas en .env")
    load_dotenv(override=True)
    return True


def prompt_for_credentials_gui() -> bool:
    """Prompt the user via Tkinter dialogs for Blizzard credentials."""
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
            messagebox.showinfo("Kezan Protocol", "Credenciales guardadas correctamente")
            load_dotenv(override=True)
            return True
        if "Network error" in error:
            messagebox.showerror("Kezan Protocol", error)
            return False
        messagebox.showerror("Kezan Protocol", "Credenciales inválidas, intenta de nuevo")


def save_env_file(data: Dict[str, str]) -> None:
    """Write the provided credentials to the .env file."""
    lines = [f"{key}={value}\n" for key, value in data.items()]
    ENV_PATH.write_text("".join(lines))


def ensure_credentials(use_gui: bool = False) -> bool:
    """Ensure valid Blizzard credentials are available.

    Returns ``True`` if credentials are valid or have been obtained
    successfully.  Returns ``False`` if the user cancels the process or a
    connection error occurs.
    """

    if check_credentials_validity():
        return True

    if use_gui:
        return prompt_for_credentials_gui()
    return prompt_for_credentials_console()
