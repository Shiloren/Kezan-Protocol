import json
from pathlib import Path

from kezan.ai_controller import AIController, AIControllerConfig


def test_can_make_request_rate_limit():
    cfg = AIControllerConfig(max_requests_per_minute=1, auto_learn=False)
    ai = AIController(cfg)
    assert ai._can_make_request() is True
    # Second within same minute should be False
    assert ai._can_make_request() is False


def test_validate_operation_allowlist():
    cfg = AIControllerConfig(allowed_operations=["read"], auto_learn=False)
    ai = AIController(cfg)
    assert ai._validate_operation({"operation": "read"}) is True
    assert ai._validate_operation({"operation": "write"}) is False


def test_validate_file_access_inside_repo(tmp_path):
    ai = AIController(AIControllerConfig(auto_learn=False))
    # project_dir is two levels up from ai_controller.py
    project_dir = Path(__file__).resolve().parents[1]
    target = project_dir / "tmp_ai_test.txt"
    target.write_text("ok", encoding="utf-8")
    try:
        assert ai._validate_file_access(str(target)) is True
    finally:
        target.unlink(missing_ok=True)


def test_load_memory_missing_file(tmp_path):
    cfg = AIControllerConfig(memory_file=str(tmp_path / "nope.json"), auto_learn=False)
    ai = AIController(cfg)
    mem = ai._load_memory()
    assert mem == {}


def test_save_memory_and_generate_key(tmp_path):
    memfile = tmp_path / "mem.json"
    cfg = AIControllerConfig(memory_file=str(memfile), auto_learn=False)
    ai = AIController(cfg)
    ai.memory = {"x": 1}
    ai._save_memory()
    assert memfile.is_file()
    data = json.loads(memfile.read_text(encoding="utf-8"))
    assert data == {"x": 1}

    key = ai._generate_memory_key({"operation": "scan", "type": "query"})
    assert key.startswith("scan_query_")


def test_calculate_success_rate():
    ai = AIController(AIControllerConfig(auto_learn=False))
    assert ai._calculate_success_rate({}, {"ok": True}) == 1.0
    assert ai._calculate_success_rate({}, {"error": "x"}) == 0.0
