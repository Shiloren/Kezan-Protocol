import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from kezan.changelog import log_change
from kezan.version import __version__


def test_log_change(tmp_path):
    os.chdir(tmp_path)
    log_change("initial entry", "0.1.0")
    content = (tmp_path / "CHANGELOG.md").read_text()
    assert "0.1.0" in content and "initial entry" in content


def test_version_cli():
    out = subprocess.check_output(
        [sys.executable, "-m", "kezan.version"], cwd=ROOT
    ).decode().strip()
    assert out == __version__

