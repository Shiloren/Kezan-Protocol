"""Utilities for exporting analysis results."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Dict, Any


def export_data(items: Iterable[Dict[str, Any]], filename: str) -> None:
    """Export ``items`` to ``filename``.

    The format is determined by the file extension.  Supported formats are
    ``.json`` and ``.csv``.
    """
    path = Path(filename)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(list(items), ensure_ascii=False, indent=2))
    elif path.suffix.lower() == ".csv":
        items_iter = list(items)
        if not items_iter:
            path.write_text("")
            return
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(items_iter[0].keys()))
            writer.writeheader()
            writer.writerows(items_iter)
    else:
        raise ValueError("Formato de exportación no soportado")
