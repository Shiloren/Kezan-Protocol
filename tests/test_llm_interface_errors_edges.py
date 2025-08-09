import types
import pytest

import kezan.llm_interface as mod


class BadResp:
    def __init__(self, data):
        self._data = data
    def json(self):
        # Return a dict without expected keys to trigger KeyError path
        return {"unexpected": True}
    def raise_for_status(self):
        pass


def test_analyze_items_with_llm_invalid_json_raises(monkeypatch):
    class MockHTTPX:
        HTTPError = RuntimeError
        @staticmethod
        def post(*a, **k):
            return BadResp({})
    monkeypatch.setattr(mod, "httpx", MockHTTPX)
    with pytest.raises(RuntimeError):
        mod.analyze_items_with_llm([{ "x": 1 }])


def test_analyze_recipes_with_inventory_changes_prompt(monkeypatch):
    # Ensure that inventory text presence doesn't crash and returns cleaned text
    class OkResp:
        def __init__(self):
            self._data = {"response": "hola"}
        def json(self):
            return self._data
        def raise_for_status(self):
            pass
    # Patch httpx and sanitize_dsl_text to observe call
    def fake_post(*a, **k):
        # assert prompt contains inventory phrase
        payload = k.get("json") or {}
        assert "prompt" in payload and "inventario" in payload["prompt"].lower()
        return OkResp()
    monkeypatch.setattr(mod, "httpx", types.SimpleNamespace(post=fake_post))
    out = mod.analyze_recipes_with_llm([{ "r": 1 }], inventory=[1, 2])
    assert out == "hola"
