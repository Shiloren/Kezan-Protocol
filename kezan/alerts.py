"""Simple threshold-based alert system."""
from __future__ import annotations

from typing import Iterable, Dict, Any, Callable


def check_margins(
    items: Iterable[Dict[str, Any]],
    threshold: float,
    notifier: Callable[[str], None] | None = None,
) -> None:
    """Notify when an item's margin exceeds ``threshold``.

    Parameters
    ----------
    items:
        Iterable of item dictionaries that contain ``name`` and ``margin`` keys.
    threshold:
        Minimum margin (e.g. ``0.3`` for 30%) required to trigger a notification.
    notifier:
        Optional callable used to deliver messages.  Defaults to :func:`print`.
    """
    notify = notifier or print
    alerts = (
        f"{item.get('name', 'Unknown')} tiene un margen de {item.get('margin', 0)*100:.0f}%"
        for item in items
        if item.get("margin", 0) > threshold
    )
    for message in alerts:
        notify(message)
