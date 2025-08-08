"""Cache sencillo con TTL opcionalmente persistente en disco."""

import os
import shelve
import time
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path(os.path.expanduser("~/.kezan"))
CACHE_FILE = CACHE_DIR / "cache.db"

_cache_memory: dict[str, tuple[Any, float]] = {}


def _open_db():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return shelve.open(str(CACHE_FILE))


def set(key: str, value: Any, ttl: int) -> None:
    """Guarda un valor con tiempo de vida (segundos).

    Parámetros:
    - key (str): clave identificadora.
    - value (Any): valor a almacenar.
    - ttl (int): tiempo de expiración en segundos.
    """
    expires = time.time() + ttl
    _cache_memory[key] = (value, expires)
    with _open_db() as db:
        db[key] = (value, expires)


def get(key: str) -> Optional[Any]:
    """Recupera un valor si no ha expirado.

    Parámetros:
    - key (str): clave a consultar.

    Retorna:
    - Any | None: valor almacenado o ``None`` si no existe o expiró.
    """
    now = time.time()
    entry = _cache_memory.get(key)
    if entry and entry[1] > now:
        return entry[0]

    with _open_db() as db:
        if key in db:
            value, expires = db[key]
            if expires > now:
                _cache_memory[key] = (value, expires)
                return value
            del db[key]
    return None
