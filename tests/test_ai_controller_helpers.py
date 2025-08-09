import json
from pathlib import Path
import pytest

from kezan.ai_controller import AIController, AIControllerConfig


def test__read_file_json_and_text(tmp_path):
    cfg = AIControllerConfig(memory_file=str(tmp_path/"m.json"))
    ctl = AIController(cfg)
    # Create JSON
    p = Path(__file__).resolve().parents[1] / "tmp_ai_read.json"
    p.write_text(json.dumps({"a": 1}), encoding="utf-8")
    try:
        out = ctl._read_file(str(p))
        assert out.get("json", {}).get("a") == 1
        # Write non-JSON and read
        p.write_text("plain", encoding="utf-8")
        out2 = ctl._read_file(str(p))
        assert "content" in out2 and "json" not in out2
    finally:
        try:
            p.unlink()
        except OSError:
            pass


def test__write_file_text_and_json(tmp_path):
    cfg = AIControllerConfig(memory_file=str(tmp_path/"m.json"))
    ctl = AIController(cfg)
    p = Path(__file__).resolve().parents[1] / "tmp_ai_write2.txt"
    try:
        o = ctl._write_file(str(p), {"k": True})
        assert o.get("written") is True and p.exists()
        o2 = ctl._write_file(str(p), "hola")
        assert o2.get("written") is True
    finally:
        try:
            p.unlink()
        except OSError:
            pass
