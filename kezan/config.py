import os
from dotenv import load_dotenv

load_dotenv()

API_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID", "")
API_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET", "")
REGION = os.getenv("REGION", "eu")
REALM_ID = os.getenv("REALM_ID", "1080")  # Ejemplo: Sanguino
