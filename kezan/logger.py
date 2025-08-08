import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

LOG_DIR = Path(os.path.expanduser("~/.kezan"))
LOG_FILE = LOG_DIR / "kezan.log"


def get_logger(name: str = "kezan") -> logging.Logger:
    """Return a configured logger instance.

    The logger writes to both a rotating file handler and the console. The
    configuration is applied only once per logger name.
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
