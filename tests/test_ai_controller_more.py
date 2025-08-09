import asyncio
from pathlib import Path

import pytest

from kezan.ai_controller import AIController, AIControllerConfig


class DummyLLMWrite:
    async def analyze_intent(self, query: str):
        if "write" in query:
            return {
                "type": "file",
                "operation": "write",
                "requires_api_call": False,
                "requires_file_access": True,
                "file_path": str(Path(__file__).resolve().parents[1] / "tmp_ai_write.txt"),
                "data": {"x": 1},
            }
        if "badop" in query:
            return {
                "type": "file",
                "operation": "delete",
                "requires_api_call": False,
                "requires_file_access": True,
                "file_path": str(Path(__file__).resolve()),
            }
        return {
            "type": "file",
            "operation": "read",
            "requires_api_call": False,
            "requires_file_access": True,
            "file_path": "C:/should/not/access/outside.txt",
        }


@pytest.mark.asyncio
async def test_ai_controller_write_and_errors(tmp_path):
    ai = AIController(AIControllerConfig(auto_learn=False, memory_file=str(tmp_path/"m.json")))
    ai.llm = DummyLLMWrite()

    # Write inside repo
    res = await ai.process_request("please write")
    assert res.get("written") is True

    # Unsupported operation path
    res2 = await ai.process_request("badop")
    assert "error" in res2

    # Invalid file access (outside of repo) -> permission error caught at top level
    res3 = await ai.process_request("read outside")
    assert res3.get("status") == "failed" and "Acceso denegado" in res3.get("error", "")
