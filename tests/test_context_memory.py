import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan.context_memory import append_context, load_context


def test_context_storage(tmp_path):
    path = tmp_path / "ctx.json"
    append_context({"x": 1}, path)
    append_context({"x": 2}, path)
    data = load_context(path)
    assert [e["x"] for e in data] == [1, 2]
