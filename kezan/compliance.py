"""Blizzard-safe compliance utilities: advisory-only guardrails for DSL and LLM outputs.

This module centralizes the constraints that ensure the app stays in a read-only/advisory mode
and never attempts client automation. Use the preamble in prompts and sanitize/validate outputs.
"""

from __future__ import annotations

import logging
from typing import List
import re

logger = logging.getLogger(__name__)

# Allowed advisory actions in the DSL
ALLOWED_ADVISORY_ACTIONS = {
    "RECOMMEND_BUY",
    "RECOMMEND_CRAFT",
    "SET",
    "ALERT",
    "WATCHLIST",
    "SIMULATE",
    "SKIP",
    "NOTIFY",
    "OPEN_AH_SEARCH",
    "COPY_POST_STRING",
}

# Prohibited (non-compliant) executive actions
PROHIBITED_ACTIONS = {
    "BUY",
    "CRAFT",
    "CANCEL",
    "POST",
    "REPOST",
    "UNDERCUT",
    "AUTOBUY",
    "AUTOCRAFT",
    "AUTOCANCEL",
    "AUTOREPOST",
}


def advisory_preamble() -> str:
    """Spanish preamble to prepend to all LLM prompts to enforce advisory-only behavior."""
    return (
        "Modo asesor Blizzard-safe: La IA solo analiza y recomienda. "
        "No generes instrucciones para automatizar acciones ni controles del cliente. "
        "Usa SOLO acciones DSL permitidas: RECOMMEND_BUY(qty,target,eta_h), "
        "RECOMMEND_CRAFT(qty,target,eta_h), SET(key,value), ALERT(type,msg), WATCHLIST(tag), "
        "SIMULATE(days,strategy), SKIP(reason), NOTIFY(channel), OPEN_AH_SEARCH(query), "
        "COPY_POST_STRING(text). Acciones prohibidas: BUY, CRAFT, CANCEL, POST, REPOST, UNDERCUT, "
        "AUTOBUY, AUTOCRAFT y similares. Si debes proponer una acción, hazlo en modo asesor."
    )


def sanitize_dsl_text(text: str) -> str:
    """Replace executive actions with advisory equivalents and warn on other prohibited terms.

    - BUY( -> RECOMMEND_BUY(
    - CRAFT( -> RECOMMEND_CRAFT(
    - Logs a warning if other prohibited tokens are present.
    """
    if not text:
        return text

    # Replace case-insensitively and tolerate optional spaces before '('
    replaced = re.sub(r"\bBUY\s*\(", "RECOMMEND_BUY(", text, flags=re.IGNORECASE)
    replaced = re.sub(r"\bCRAFT\s*\(", "RECOMMEND_CRAFT(", replaced, flags=re.IGNORECASE)

    found = detect_prohibited_actions(replaced)
    # BUY/CRAFT already replaced; ignore if only these two were in the original text
    residual = [t for t in found if t not in {"BUY", "CRAFT"}]
    if residual:
        logger.warning("Acciones no permitidas detectadas en salida LLM: %s", ", ".join(sorted(set(residual))))
    return replaced


def detect_prohibited_actions(text: str) -> List[str]:
    """Return list of prohibited action tokens as standalone actions (e.g., BUY(, CRAFT().

    Avoid false positives like RECOMMEND_BUY by requiring the token to be followed by '('
    and not preceded by an uppercase letter or underscore.
    """
    hits: List[str] = []
    if not text:
        return hits
    for token in sorted(PROHIBITED_ACTIONS):
        pattern = rf"(?<![A-Z_]){re.escape(token)}\s*\("
        if re.search(pattern, text):
            hits.append(token)
    return hits
