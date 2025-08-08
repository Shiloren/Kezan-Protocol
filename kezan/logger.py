"""Logging utilities used across the Kezan Protocol package.

The module exposes a single helper :func:`get_logger` which returns a
configured :class:`logging.Logger` instance writing to both a rotating file
and the console.  The configuration is idempotent, meaning repeated calls
with the same ``name`` reuse existing handlers.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

LOG_DIR = Path(os.path.expanduser("~/.kezan"))
LOG_FILE = LOG_DIR / "kezan.log"


def get_logger(name: str = "kezan") -> logging.Logger:
    """Return a configured :class:`logging.Logger`.

    Args:
        name: Name of the logger to retrieve or create.

    Returns:
        logging.Logger: Logger with file and stream handlers attached.

    Notes:
        Subsequent calls with the same ``name`` will reuse the same logger
        instance and not add duplicate handlers.
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
