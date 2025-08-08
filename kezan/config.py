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
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Read configuration values with sensible defaults
API_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID", "")
API_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET", "")
REGION = os.getenv("REGION", "eu")
REALM_ID = os.getenv("REALM_ID", "1080")  # Ejemplo: Sanguino
