import importlib
import os
import sys

# Ensure package can be imported when tests run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan import logger as logger_module


def test_logger_writes(tmp_path, monkeypatch):
    """Logger writes messages to a rotating file."""

    # -- Setup -----------------------------------------------------------------
    log_file = tmp_path / "kezan.log"
    importlib.reload(logger_module)  # Reload to apply monkeypatching
    monkeypatch.setattr(logger_module, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logger_module, "LOG_FILE", log_file)

    # -- Exercise --------------------------------------------------------------
    log = logger_module.get_logger("test")
    log.info("hello world")

    # -- Flush handlers to ensure data is written ------------------------------
    for handler in log.handlers:
        handler.flush()

    # -- Verify ----------------------------------------------------------------
    assert log_file.exists(), "Log file was not created"
    content = log_file.read_text()
    print("log content:", content)
    assert "hello world" in content
