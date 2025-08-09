"""
Configuration module for Kezan Protocol.

This module uses `python-dotenv` to load environment variables from a `.env` file.
It exposes four configuration constants that can be overridden via environment variables:

- ``API_CLIENT_ID``: Blizzard API client ID.
- ``API_CLIENT_SECRET``: Blizzard API client secret.
- ``REGION``: Blizzard API region (e.g. "eu", "us").
- ``REALM_ID``: Connected realm ID for auction data.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Read configuration values with sensible defaults (support both prefixes)
API_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID") or os.getenv("BLIZZARD_CLIENT_ID", "")
API_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET") or os.getenv("BLIZZARD_CLIENT_SECRET", "")
REGION = os.getenv("REGION", "eu")
REALM_ID = os.getenv("REALM_ID", "1080")  # Ejemplo: Sanguino

# Path where local LLM templates are stored
LOCAL_MODELS_PATH = os.getenv(
    "LOCAL_MODELS_PATH", os.path.expanduser("~/.kezan/models")
)


def has_blizzard_credentials() -> bool:
    """Return True if Blizzard API credentials are defined."""
    return bool(API_CLIENT_ID and API_CLIENT_SECRET and REGION)


def validate_local_model_path(path: str | None = None) -> bool:
    """Validate that a local model directory exists."""
    target = Path(path or LOCAL_MODELS_PATH)
    return target.is_dir()
