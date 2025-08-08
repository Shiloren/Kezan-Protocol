"""Herramientas para gestionar el contexto persistente de análisis.

Las entradas se almacenan en disco mediante JSON. Para evitar crecimiento
indefinido se aplican dos políticas configurables mediante variables de
entorno:

``CTX_MAX_ENTRIES``
    Número máximo de entradas a conservar; las más antiguas se descartan.

``CTX_MAX_DAYS``
    Antigüedad máxima permitida en días; se eliminan entradas más viejas.

Las entradas se marcan con marca de tiempo y se limpian automáticamente al
cargarse o actualizarse. También se puede importar contexto desde un archivo
CSV.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_PATH = Path.home() / ".kezan" / "context.json"


def _get_limits() -> tuple[int, int]:
    """Obtiene los límites de poda desde variables de entorno.

    Retorna:
    - tuple[int, int]: ``(max_entries, max_days)``.
    """
    max_entries = int(os.getenv("CTX_MAX_ENTRIES", "100"))
    max_days = int(os.getenv("CTX_MAX_DAYS", "30"))
    return max_entries, max_days


def _clean(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Elimina entradas que exceden los límites configurados."""
    max_entries, max_days = _get_limits()
    if max_days > 0:
        cutoff = datetime.utcnow() - timedelta(days=max_days)
        cleaned: List[Dict[str, Any]] = []
        for entry in data:
            ts = entry.get("timestamp")
            if not ts:
                cleaned.append(entry)
                continue
            try:
                if datetime.fromisoformat(ts) >= cutoff:
                    cleaned.append(entry)
            except ValueError:
                cleaned.append(entry)
        data = cleaned
    if max_entries > 0 and len(data) > max_entries:
        data = data[-max_entries:]
    return data


def load_context(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Carga el contexto almacenado aplicando las políticas de limpieza."""
    p = Path(path) if path else _DEFAULT_PATH
    if p.exists():
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            data = []
    else:
        data = []
    data = _clean(data)
    if data:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data


def append_context(entry: Dict[str, Any], path: Optional[str] = None) -> None:
    """Agrega una nueva entrada de análisis al contexto."""
    entry = dict(entry)
    entry.setdefault("timestamp", datetime.utcnow().isoformat())
    data = load_context(path)
    data.append(entry)
    data = _clean(data)
    p = Path(path) if path else _DEFAULT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_context_from_csv(csv_path: str, path: Optional[str] = None) -> None:
    """Carga entradas de contexto desde un CSV y las fusiona con las existentes."""
    dest = Path(path) if path else _DEFAULT_PATH
    rows: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts = row.get("timestamp")
            if not ts:
                continue
            try:
                datetime.fromisoformat(ts)
            except ValueError:
                continue
            rows.append(row)
    if not rows:
        return
    data = load_context(dest)
    data.extend(rows)
    data = _clean(data)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2))
