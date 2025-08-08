import csv
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan.context_memory import append_context, load_context, load_context_from_csv


def test_context_limit_entries(tmp_path, monkeypatch):
    monkeypatch.setenv("CTX_MAX_ENTRIES", "2")
    path = tmp_path / "ctx.json"
    append_context({"x": 1}, path)
    append_context({"x": 2}, path)
    append_context({"x": 3}, path)
    data = load_context(path)
    assert [e["x"] for e in data] == [2, 3]


def test_context_age_cleanup(tmp_path, monkeypatch):
    monkeypatch.setenv("CTX_MAX_DAYS", "7")
    path = tmp_path / "ctx.json"
    old = {"x": 1, "timestamp": (datetime.utcnow() - timedelta(days=10)).isoformat()}
    new = {"x": 2, "timestamp": datetime.utcnow().isoformat()}
    path.write_text(json.dumps([old, new], ensure_ascii=False))
    data = load_context(path)
    assert len(data) == 1 and data[0]["x"] == 2


def test_load_context_from_csv(tmp_path):
    json_path = tmp_path / "ctx.json"
    csv_path = tmp_path / "ctx.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp", "x"])
        writer.writeheader()
        writer.writerow({"timestamp": datetime.utcnow().isoformat(), "x": "1"})
        writer.writerow({"x": "2"})  # invalid, no timestamp
    load_context_from_csv(csv_path, json_path)
    data = load_context(json_path)
    assert len(data) == 1 and data[0]["x"] == "1"
