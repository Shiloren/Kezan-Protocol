import importlib
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan import logger as logger_module


def test_logger_writes(tmp_path, monkeypatch):
    log_file = tmp_path / "kezan.log"
    importlib.reload(logger_module)
    monkeypatch.setattr(logger_module, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logger_module, "LOG_FILE", log_file)

    log = logger_module.get_logger("test")
    log.info("hello world")

    for handler in log.handlers:
        handler.flush()

    assert log_file.exists()
    assert "hello world" in log_file.read_text()
