"""Utilidades de logging usadas en todo Kezan Protocol.

El módulo expone un único helper :func:`get_logger` que devuelve un
``logging.Logger`` configurado para escribir tanto en archivo rotativo como en
consola. La configuración es idempotente: llamadas repetidas reutilizan los
handlers existentes.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

LOG_DIR = Path(os.path.expanduser("~/.kezan"))
LOG_FILE = LOG_DIR / "kezan.log"


def get_logger(name: str = "kezan") -> logging.Logger:
    """Devuelve un :class:`logging.Logger` configurado.

    Parámetros:
    - name (str): nombre del logger a obtener o crear.

    Retorna:
    - logging.Logger: logger con manejadores de archivo y consola.

    Notas:
    - Llamadas posteriores con el mismo nombre reutilizan la instancia.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
