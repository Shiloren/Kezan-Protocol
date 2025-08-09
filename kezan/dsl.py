"""DSL parser and validator for Kezan Protocol (advisory-only mode).

Supports blocks:

RULE "<nombre>"
WHEN <condicion>
THEN <acciones separadas por ;>
WITH <clave=valor, ...>

Parses actions to a structured form and validates allowed advisory actions.
Condition is kept as a normalized string for now; a full AST can be added later.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .compliance import ALLOWED_ADVISORY_ACTIONS, PROHIBITED_ACTIONS


@dataclass
class Action:
    name: str
    args: Dict[str, object] = field(default_factory=dict)
    posargs: List[object] = field(default_factory=list)


@dataclass
class DSLRule:
    name: str
    condition: str
    actions: List[Action]
    metadata: Dict[str, object] = field(default_factory=dict)


class DSLParseError(ValueError):
    pass


def parse_rules(text: str) -> List[DSLRule]:
    """Parse one or more rules from text.

    Returns a list of DSLRule. Raises DSLParseError for malformed inputs.
    """
    if not text:
        return []

    # Normalize line endings and strip trailing spaces
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    i = 0
    n = len(lines)
    rules: List[DSLRule] = []

    any_content = any(ln.strip() for ln in lines)
    saw_rule = False
    while i < n:
        # Seek RULE line
        while i < n and not lines[i].strip().startswith("RULE "):
            i += 1
        if i >= n:
            break
        m = re.match(r"^RULE\s+\"(.+?)\"\s*$", lines[i].strip())
        if not m:
            raise DSLParseError(f"Línea RULE inválida: {lines[i]}")
        name = m.group(1)
        saw_rule = True
        i += 1

        # WHEN block (single line or multi-line until THEN)
        if i >= n or not lines[i].strip().startswith("WHEN"):
            raise DSLParseError(f"Se esperaba WHEN tras RULE '{name}'")
        cond_parts: List[str] = []
        while i < n and not lines[i].strip().startswith("THEN"):
            cond_parts.append(lines[i].strip().removeprefix("WHEN").strip())
            i += 1
            if i < n and lines[i].strip() == "":
                i += 1
                break
        condition = " ".join([p for p in cond_parts if p])

        if i >= n or not lines[i].strip().startswith("THEN"):
            raise DSLParseError(f"Se esperaba THEN en la regla '{name}'")

        # THEN block: capture inline actions on the same line (after THEN) and continue until WITH/RULE
        then_lines: List[str] = []
        inline = lines[i].strip()[4:].strip()  # text after 'THEN'
        if inline:
            then_lines.append(inline)
        i += 1
        while i < n and not lines[i].strip().startswith("WITH") and not lines[i].strip().startswith("RULE "):
            if lines[i].strip():
                then_lines.append(lines[i].strip())
            i += 1
        then_text = " ".join(then_lines)
        # Split actions by ';'
        raw_actions = [a.strip() for a in then_text.split(";") if a.strip()]
        actions = [parse_action(a) for a in raw_actions]

        metadata: Dict[str, object] = {}
        if i < n and lines[i].strip().startswith("WITH"):
            meta_text = lines[i].strip().removeprefix("WITH").strip()
            metadata = parse_kv_list(meta_text)
            i += 1

        rules.append(DSLRule(name=name, condition=normalize_condition(condition), actions=actions, metadata=metadata))

    if not saw_rule and any_content:
        # Content present but no RULE found → estructura inválida
        raise DSLParseError("No se encontró ningún bloque RULE válido")
    return rules


def parse_action(text: str) -> Action:
    m = re.match(r"^([A-Z_]+)\s*\((.*)\)\s*$", text)
    if not m:
        raise DSLParseError(f"Acción inválida: {text}")
    name = m.group(1)
    args_text = m.group(2).strip()
    args: Dict[str, object] = {}
    posargs: List[object] = []
    if args_text:
        for part in split_commas(args_text):
            if '=' in part:
                k, v = split_kv(part)
                args[k] = parse_value(v)
            else:
                posargs.append(parse_value(part))
    return Action(name=name, args=args, posargs=posargs)


def split_commas(s: str) -> List[str]:
    parts: List[str] = []
    buf = []
    depth = 0
    in_str = False
    quote = ""
    for ch in s:
        if in_str:
            buf.append(ch)
            if ch == quote:
                in_str = False
        else:
            if ch in ('\"', "\'"):
                in_str = True
                quote = ch
                buf.append(ch)
            elif ch == '(':
                depth += 1
                buf.append(ch)
            elif ch == ')':
                depth = max(0, depth - 1)
                buf.append(ch)
            elif ch == ',' and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def split_kv(s: str) -> tuple[str, str]:
    if '=' not in s:
        raise DSLParseError(f"Argumento sin '=': {s}")
    k, v = s.split('=', 1)
    return k.strip(), v.strip()


def parse_kv_list(s: str) -> Dict[str, object]:
    return {k: parse_value(v) for k, v in (split_kv(p) for p in split_commas(s))}


def parse_value(s: str) -> object:
    # String literal
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    # Booleans
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    # Numbers (int/float)
    try:
        if re.match(r"^-?\d+$", s):
            return int(s)
        if re.match(r"^-?\d*\.\d+$", s):
            return float(s)
    except Exception:
        pass
    # Identifiers/expressions remain as raw strings (e.g., p50_7d*0.98, MIN(...))
    return s


def normalize_condition(cond: str) -> str:
    # Collapse whitespace and standardize operators spacing
    c = re.sub(r"\s+", " ", cond).strip()
    return c


def validate_rules(rules: List[DSLRule]) -> List[str]:
    """Validate advisory-only constraints and basic structure; return list of issues."""
    issues: List[str] = []
    for r in rules:
        if not r.name:
            issues.append("Regla sin nombre")
        if not r.condition:
            issues.append(f"Regla '{r.name}' sin condición")
        if not r.actions:
            issues.append(f"Regla '{r.name}' sin acciones")
        for a in r.actions:
            if a.name in PROHIBITED_ACTIONS:
                issues.append(f"Acción prohibida en '{r.name}': {a.name}")
            if a.name not in ALLOWED_ADVISORY_ACTIONS:
                # Allow unknown advisory extensions prefixed with RECOMMEND_ as soft-warning
                if not a.name.startswith("RECOMMEND_") and a.name not in {"ALERT", "WATCHLIST", "SIMULATE", "SET", "SKIP", "NOTIFY", "OPEN_AH_SEARCH", "COPY_POST_STRING"}:
                    issues.append(f"Acción no permitida/inesperada en '{r.name}': {a.name}")
    return issues
