import json
import types
import pytest

from kezan.llm_interface import LLMInterface


class DummyResp:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise RuntimeError("status error")


@pytest.mark.asyncio
async def test__post_async_ollama(monkeypatch):
    llm = LLMInterface()
    llm.api_url = "http://localhost:11434/api/generate"

    async def fake_post(self, url, json=None, headers=None, timeout=None):
        return DummyResp({"response": "hola"})

    class FakeClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None, timeout=None):
            return await fake_post(self, url, json=json, headers=headers, timeout=timeout)

    import kezan.llm_interface as mod
    monkeypatch.setattr(mod, "httpx", types.SimpleNamespace(AsyncClient=FakeClient, post=lambda *a, **k: DummyResp({"response": "hola"})))

    out = await llm._post_async("hola")
    assert out == "hola"


@pytest.mark.asyncio
async def test__post_async_openai(monkeypatch):
    llm = LLMInterface()
    llm.api_url = "http://localhost:1234/v1/chat/completions"

    openai_like = {
        "choices": [
            {"message": {"content": "respuesta"}}
        ]
    }

    async def fake_post(self, url, json=None, headers=None, timeout=None):
        return DummyResp(openai_like)

    class FakeClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None, timeout=None):
            return await fake_post(self, url, json=json, headers=headers, timeout=timeout)

    import kezan.llm_interface as mod
    monkeypatch.setattr(mod, "httpx", types.SimpleNamespace(AsyncClient=FakeClient, post=lambda *a, **k: DummyResp(openai_like)))

    out = await llm._post_async("hola")
    assert out == "respuesta"


def test__post_sync_and_payload_headers(monkeypatch):
    llm = LLMInterface()
    llm.api_url = "http://localhost:11434/api/generate"

    # Verify payload shape for Ollama
    cfg = llm._build_payload_headers("p")
    assert "prompt" in cfg["payload"]
    assert "messages" not in cfg["payload"]

    import kezan.llm_interface as mod
    monkeypatch.setattr(mod, "httpx", types.SimpleNamespace(post=lambda *a, **k: DummyResp({"response": "sync"})))

    out = llm._post_sync("hola")
    assert out == "sync"

    # Verify OpenAI style payload
    llm.api_url = "http://local/v1/chat/completions"
    cfg2 = llm._build_payload_headers("p2")
    assert "messages" in cfg2["payload"]
    assert "prompt" not in cfg2["payload"]


@pytest.mark.asyncio
async def test_analyze_intent_success_and_fallback(monkeypatch):
    llm = LLMInterface()

    async def good_post(self, url, json=None, headers=None, timeout=None):
        return DummyResp({"response": json["prompt"].split("\n")[-1]})

    class FakeClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None, timeout=None):
            return await good_post(self, url, json=json, headers=headers, timeout=timeout)

    import kezan.llm_interface as mod
    # Return proper JSON
    monkeypatch.setattr(mod, "httpx", types.SimpleNamespace(AsyncClient=FakeClient))
    # Craft response to be a JSON string
    async def fake__post_async(prompt: str, timeout: int = 30):
        return json.dumps({"type": "query", "operation": "read", "requires_api_call": False, "requires_file_access": False})
    monkeypatch.setattr(LLMInterface, "_post_async", staticmethod(fake__post_async))
    intent = await llm.analyze_intent("hola")
    assert intent.get("type") == "query"

    # Fallback path: not JSON
    async def fake_bad(prompt: str, timeout: int = 30):
        return "texto plano"
    monkeypatch.setattr(LLMInterface, "_post_async", staticmethod(fake_bad))
    intent2 = await llm.analyze_intent("hola")
    assert intent2.get("type") == "unknown"


@pytest.mark.asyncio
async def test_scan_auction_house_cleaning(monkeypatch):
    llm = LLMInterface()

    items = [
        {"item_id": 1, "price": 10, "quantity": 2},
        {"item_id": 2, "price": 11},  # missing quantity
        [1, 2, 3],  # invalid
    ]

    async def fake_post(prompt: str, timeout: int = 45):
        return json.dumps(items)

    monkeypatch.setattr(LLMInterface, "_post_async", staticmethod(fake_post))

    out = await llm.scan_auction_house([{"x": 1}], {"pref": True}, "retail")
    assert out == [{"item_id": 1, "price": 10, "quantity": 2}]


def test_suggest_search_strategy_fallback(monkeypatch):
    llm = LLMInterface()

    def boom(prompt: str, timeout: int = 20):
        raise RuntimeError("boom")

    monkeypatch.setattr(LLMInterface, "_post_sync", staticmethod(boom))
    txt = llm.suggest_search_strategy([], [], "retail")
    assert isinstance(txt, str) and len(txt) > 0


@pytest.mark.asyncio
async def test_analyze_market_opportunity_paths(monkeypatch):
    llm = LLMInterface()

    async def ok(prompt: str, timeout: int = 30):
        return json.dumps({"analysis": "a", "opportunity": True, "reason": "r"})

    monkeypatch.setattr(LLMInterface, "_post_async", staticmethod(ok))
    r = await llm.analyze_market_opportunity({"a": 1}, [])
    assert r.get("opportunity") is True

    async def bad(prompt: str, timeout: int = 30):
        raise RuntimeError("x")

    monkeypatch.setattr(LLMInterface, "_post_async", staticmethod(bad))
    r2 = await llm.analyze_market_opportunity({"a": 1}, [])
    assert r2.get("opportunity") is False and "reason" in r2
