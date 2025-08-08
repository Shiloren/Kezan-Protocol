import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kezan.export import export_data


def test_export_json(tmp_path):
    data = [{"a": 1}, {"a": 2}]
    path = tmp_path / "out.json"
    export_data(data, path)
    assert path.exists()
    assert "\n" in path.read_text()


def test_export_csv(tmp_path):
    data = [{"a": 1}, {"a": 2}]
    path = tmp_path / "out.csv"
    export_data(data, path)
    content = path.read_text().splitlines()
    assert content[0] == "a"
    assert content[1] == "1"
