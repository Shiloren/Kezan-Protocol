"""Parser de SavedVariables Lua -> JSON para Kezan Protocol.

Nota: Este parser es mínimo; asume la estructura propuesta en docs/addon-spec.md.
Para usos avanzados podría integrarse `lupa` o `slpp`. Aquí resolvemos claves y
valores básicos (números, strings simples, tablas anidadas con llaves numéricas).
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict

_TABLE_RE = re.compile(r"KezanAHDB\s*=\s*\{(.*)\}\s*\Z", re.S)


def parse_savedvariables(lua_text: str) -> Dict[str, Any]:
    """Extrae una estructura básica de KezanAHDB.

    Este parser tolera espacios y comentarios sencillos `--`. No ejecuta código.
    """
    if not lua_text:
        return {}
    # eliminar comentarios de línea
    cleaned = re.sub(r"--.*", "", lua_text)
    m = _TABLE_RE.search(cleaned)
    if not m:
        return {}
    body = m.group(1)

    # heurística simple: localizar bloques de items y playerStats
    result: Dict[str, Any] = {}

    # lastScan, realm, faction
    last = re.search(r"lastScan\s*=\s*(\d+)", body)
    if last:
        result["lastScan"] = int(last.group(1))
    realm = re.search(r"realm\s*=\s*\"([^\"]+)\"", body)
    if realm:
        result["realm"] = realm.group(1)
    faction = re.search(r"faction\s*=\s*\"([^\"]+)\"", body)
    if faction:
        result["faction"] = faction.group(1)

    # items: [id] = { price = 123, qty = 1, seller = "X", ts = 111 }
    items: Dict[int, Any] = {}
    for item_match in re.finditer(r"\[(\d+)\]\s*=\s*\{([^}]+)\}", body):
        item_id = int(item_match.group(1))
        obj = item_match.group(2)
        price = re.search(r"price\s*=\s*(\d+)", obj)
        qty = re.search(r"qty\s*=\s*(\d+)", obj)
        seller = re.search(r"seller\s*=\s*\"([^\"]+)\"", obj)
        ts = re.search(r"ts\s*=\s*(\d+)", obj)
        items[item_id] = {
            "price": int(price.group(1)) if price else None,
            "qty": int(qty.group(1)) if qty else None,
            "seller": seller.group(1) if seller else None,
            "ts": int(ts.group(1)) if ts else None,
        }
    if items:
        result["items"] = items

    # playerStats
    pstats = re.search(r"playerStats\s*=\s*\{([^}]+)\}", body)
    if pstats:
        ps = pstats.group(1)
        def _f(name: str) -> float | None:
            pattern = rf"{name}\s*=\s*([0-9]*\.?[0-9]+)"
            mm = re.search(pattern, ps)
            return float(mm.group(1)) if mm else None
        stats = {
            "multicraft": _f("multicraft"),
            "resourcefulness": _f("resourcefulness"),
            "inspiration": _f("inspiration"),
            "craftingSpeed": _f("craftingSpeed"),
            "skill": _f("skill"),
        }
        result["playerStats"] = stats

    return result
