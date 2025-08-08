"""Simple CHANGELOG.md management utilities."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path


def log_change(summary: str, version: str) -> None:
    """Append a change entry to ``CHANGELOG.md``.

    Each entry is stored in the format::

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
