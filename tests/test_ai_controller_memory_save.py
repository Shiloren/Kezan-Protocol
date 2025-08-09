import json
from pathlib import Path

from kezan.ai_controller import AIController, AIControllerConfig


def test_update_memory_and_save(tmp_path):
    cfg = AIControllerConfig(memory_file=str(tmp_path/"mem.json"))
    ctl = AIController(cfg)
    intent = {"operation": "read", "type": "query"}
    result = {"ok": True}
    ctl._update_memory(intent, result)
    # Memory file should exist and contain a key
    p = Path(cfg.memory_file)
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert any(v.get("result", {}).get("ok") for v in data.values())
