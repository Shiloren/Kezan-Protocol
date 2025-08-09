import json
import types
import pytest

from kezan.llm_interface import LLMInterface

class DummyResp:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json
    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise RuntimeError("status error")

@pytest.mark.asyncio
async def test_post_async_ollama(monkeypatch):
    llm = LLMInterface()
    llm.api_url = "http://localhost:11434/api/generate"  # Ollama style

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
async def test_post_async_openai(monkeypatch):
    llm = LLMInterface()
    llm.api_url = "http://localhost:1234/v1/chat/completions"  # OpenAI style

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

@pytest.mark.asyncio
async def test_analyze_intent_fallback(monkeypatch):
    llm = LLMInterface()
    llm.api_url = "http://localhost:11434/api/generate"

    async def fake_post(self, url, json=None, headers=None, timeout=None):
        # devuelve algo no JSON
        return DummyResp({"response": "texto plano"})

    class FakeClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, json=None, headers=None, timeout=None):
            return await fake_post(self, url, json=json, headers=headers, timeout=timeout)

    import kezan.llm_interface as mod
    monkeypatch.setattr(mod, "httpx", types.SimpleNamespace(AsyncClient=FakeClient, post=lambda *a, **k: DummyResp({"response": "texto plano"})))

    intent = await llm.analyze_intent("haz algo")
    assert isinstance(intent, dict)
    assert intent.get("requires_api_call") in (False, True)
