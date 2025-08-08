import os
import sys

import pytest
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan.llm_interface import analyze_items_with_llm


def test_analyze_items_with_llm_success(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": "ok"}

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    result = analyze_items_with_llm([{"name": "Black Lotus"}])
    assert result == "ok"


def test_analyze_items_with_llm_connection_error(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("fail")

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(RuntimeError) as exc:
        analyze_items_with_llm([{"name": "Black Lotus"}])

    assert "IA local" in str(exc.value)
