"""Lightweight local context storage for previous analyses."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

_DEFAULT_PATH = Path.home() / ".kezan" / "context.json"


def load_context(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load stored analysis context."""
    p = Path(path) if path else _DEFAULT_PATH
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            return []
    return []


def append_context(entry: Dict[str, Any], path: Optional[str] = None) -> None:
    """Append a new analysis ``entry`` to the context store."""
    data = load_context(path)
    data.append(entry)
    p = Path(path) if path else _DEFAULT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
