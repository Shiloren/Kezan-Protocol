import json
from pathlib import Path

import pytest

from kezan.ai_controller import AIController, AIControllerConfig


class DummyLLM:
    async def analyze_intent(self, query: str):  # pragma: no cover - specific per test
        return {}


@pytest.mark.asyncio
async def test_disallowed_operation_is_blocked(monkeypatch):
    cfg = AIControllerConfig(allowed_operations=["READ"])  # only READ allowed
    ctl = AIController(config=cfg)
    monkeypatch.setattr(ctl, "llm", DummyLLM())

    async def deny_intent(_):
        return {"operation": "DELETE", "requires_api_call": False, "requires_file_access": False}

    monkeypatch.setattr(ctl.llm, "analyze_intent", deny_intent)
    out = await ctl.process_request("delete something")
    assert out["status"] == "failed" and "Operación no permitida" in out["error"]


@pytest.mark.asyncio
async def test_api_rate_limit_violation(monkeypatch):
    cfg = AIControllerConfig(max_requests_per_minute=0)
    ctl = AIController(config=cfg)

    async def api_intent(_):
        return {"operation": "fetch", "requires_api_call": True}

    monkeypatch.setattr(ctl, "llm", DummyLLM())
    monkeypatch.setattr(ctl.llm, "analyze_intent", api_intent)
    out = await ctl.process_request("get auctions")
    assert out["status"] == "failed" and "Límite de peticiones" in out["error"]


@pytest.mark.asyncio
async def test_file_access_denied(monkeypatch):
    ctl = AIController()
    monkeypatch.setattr(ctl, "llm", DummyLLM())

    # Use an outside path to trigger permission denial
    outside = str(Path("C:/Windows/System32/drivers/etc/hosts"))

    async def file_intent(_):
        return {"operation": "read", "requires_file_access": True, "file_path": outside}

    monkeypatch.setattr(ctl.llm, "analyze_intent", file_intent)
    out = await ctl.process_request("read outside")
    assert out["status"] == "failed" and "Acceso denegado" in out["error"]


@pytest.mark.asyncio
async def test_file_read_and_write_inside_repo(monkeypatch, tmp_path):
    ctl = AIController()
    monkeypatch.setattr(ctl, "llm", DummyLLM())

    # Resolve a path inside the repo (README.md should exist)
    repo_root = Path(__file__).resolve().parents[1]
    readme = repo_root / "README.md"
    assert readme.exists()

    async def read_intent(_):
        return {"operation": "read", "requires_file_access": True, "file_path": str(readme)}

    monkeypatch.setattr(ctl.llm, "analyze_intent", read_intent)
    res = await ctl.process_request("read readme")
    assert res.get("path", "").endswith("README.md") and "content" in res

    # Write to a temp file inside repo
    target = repo_root / "tmp_ai_controller_test.json"

    async def write_intent(_):
        return {
            "operation": "write",
            "requires_file_access": True,
            "file_path": str(target),
            "data": {"ok": True},
        }

    monkeypatch.setattr(ctl.llm, "analyze_intent", write_intent)
    wres = await ctl.process_request("write file")
    assert wres.get("written") is True and target.exists()
    # Cleanup
    try:
        target.unlink()
    except OSError:
        pass
