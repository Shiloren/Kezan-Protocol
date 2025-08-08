"""Utilidades sencillas para gestionar ``CHANGELOG.md``."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path


def log_change(summary: str, version: str) -> None:
    """Agrega una entrada al ``CHANGELOG.md``.

    Cada entrada se almacena con el formato::

        ## <version> - <timestamp>
        <summary>
    """
    entry = (
        f"## {version} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{summary.strip()}\n\n"
    )
    path = Path("CHANGELOG.md")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(entry)
