import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan.alerts import check_margins


def test_check_margins_notifies():
    items = [
        {"name": "A", "margin": 0.5},
        {"name": "B", "margin": 0.1},
    ]
    messages: list[str] = []
    check_margins(items, 0.3, notifier=messages.append)
    assert messages == ["A tiene un margen de 50%"]
