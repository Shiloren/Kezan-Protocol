"""Utilities for exporting analysis results with overwrite protection."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable

from kezan.logger import get_logger

logger = get_logger(__name__)


def export_data(
    items: Iterable[Dict[str, Any]], filename: str, overwrite: bool = False
) -> Path:
    """Export ``items`` to ``filename``.

    Parameters
    ----------
    items:
        Iterable with the data to export.
    filename:
        Target filename.  If a file with the same name already exists a
        timestamp will be appended to avoid overwriting unless ``overwrite`` is
        ``True``.
    overwrite:
        When ``True`` existing files are replaced.

    Returns
    -------
    Path
        Path to the file written to disk.

    Raises
    ------
    ValueError
        If the file extension is not ``.json`` or ``.csv``.
    """

    path = Path(filename)
    if path.exists() and not overwrite:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = path.with_name(f"{path.stem}_{ts}{path.suffix}")

    if path.suffix.lower() == ".json":
        items_iter = list(items)
        path.write_text(json.dumps(items_iter, ensure_ascii=False, indent=2))
    elif path.suffix.lower() == ".csv":
        items_iter = list(items)
        if not items_iter:
            path.write_text("")
            logger.info("Exported 0 records to %s", path)
            return path
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(items_iter[0].keys()))
            writer.writeheader()
            writer.writerows(items_iter)
    else:
        raise ValueError("Formato de exportación no soportado")

    logger.info("Exported %d records to %s", len(items_iter), path)
    return path
