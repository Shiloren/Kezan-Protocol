"""Utilidades para exportar resultados de análisis con protección de sobrescritura."""

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
    """Exporta ``items`` a ``filename``.

    Parámetros:
    - items (Iterable[Dict[str, Any]]): datos a exportar.
    - filename (str): nombre de archivo destino. Si existe y ``overwrite`` es
      ``False``, se añade marca de tiempo para evitar sobrescribir.
    - overwrite (bool): si es ``True``, se reemplaza el archivo existente.

    Retorna:
    - Path: ruta del archivo generado.

    Lanza:
    - ValueError: si la extensión no es ``.json`` ni ``.csv``.
    - OSError: si ocurre un problema al escribir el archivo.
    """
    path = Path(filename)
    if path.exists() and not overwrite:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = path.with_name(f"{path.stem}_{ts}{path.suffix}")

    items_iter = list(items)
    try:
        if path.suffix.lower() == ".json":
            path.write_text(json.dumps(items_iter, ensure_ascii=False, indent=2))
        elif path.suffix.lower() == ".csv":
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
    except OSError as exc:
        logger.error("No se pudo exportar a %s: %s", path, exc)
        raise

    logger.info("Exported %d records to %s", len(items_iter), path)
    return path
