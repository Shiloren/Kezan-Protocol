import types
import importlib


def test_build_payload_headers_openai_auth(monkeypatch):
    # Set API key and reload module to pick it up
    monkeypatch.setenv("LLM_API_KEY", "k")
    import kezan.llm_interface as mod
    importlib.reload(mod)
    llm = mod.LLMInterface()
    llm.api_url = "http://local/v1/chat/completions"
    cfg = llm._build_payload_headers("p")
    assert cfg["headers"].get("Authorization", "").startswith("Bearer ")
