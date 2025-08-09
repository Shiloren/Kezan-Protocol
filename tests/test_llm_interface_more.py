import json
from pathlib import Path
import types
import pytest

import kezan.llm_interface as mod
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


def test_load_model_template_happy(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "validate_local_model_path", lambda path=None: True)
    monkeypatch.setattr(mod, "LOCAL_MODELS_PATH", tmp_path)
    (tmp_path / "x.json").write_text(json.dumps({
        "model": "mistral",
        "api_url": "http://local/v1/chat/completions",
        "temperature": 0.1,
        "top_p": 0.5
    }), encoding="utf-8")
    mod.load_model_template("x")
    # Verify globals updated
    assert mod.LLM_MODEL == "mistral"
    assert "/v1/" in mod.LLM_API_URL
    assert mod.LLM_TEMPERATURE == 0.1
    assert mod.LLM_TOP_P == 0.5


def test_load_model_template_invalid_json(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "validate_local_model_path", lambda path=None: True)
    monkeypatch.setattr(mod, "LOCAL_MODELS_PATH", tmp_path)
    (tmp_path / "bad.json").write_text("{ bad json }", encoding="utf-8")
    with pytest.raises(ValueError):
        mod.load_model_template("bad")


def test_load_model_template_missing_model_key(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "validate_local_model_path", lambda path=None: True)
    monkeypatch.setattr(mod, "LOCAL_MODELS_PATH", tmp_path)
    (tmp_path / "tmpl.json").write_text(json.dumps({"x": 1}), encoding="utf-8")
    with pytest.raises(ValueError):
        mod.load_model_template("tmpl")


def test__extract_text_variants():
    llm = LLMInterface()
    # OpenAI chat content
    j1 = {"choices": [{"message": {"content": "hola"}}]}
    assert llm._extract_text(j1) == "hola"
    # OpenAI text completion-like
    j2 = {"choices": [{"text": "texto"}]}
    assert llm._extract_text(j2) == "texto"
    # Ollama style
    j3 = {"response": "ok"}
    assert llm._extract_text(j3) == "ok"


def test__build_payload_headers_auth(monkeypatch):
    llm = LLMInterface()
    llm.api_url = "http://local/v1/chat/completions"
    # Temporarily set API key
    monkeypatch.setenv("LLM_API_KEY", "abc123")
    # Re-import module constant
    import importlib
    import kezan.llm_interface as m2
    importlib.reload(m2)
    llm2 = m2.LLMInterface()
    llm2.api_url = "http://local/v1/chat/completions"
    cfg = llm2._build_payload_headers("p")
    assert "Authorization" in cfg["headers"]
