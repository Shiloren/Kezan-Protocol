from kezan.sv_parser import parse_savedvariables
from kezan.cloud_history import CloudHistoryClient


def test_parse_savedvariables_basic():
    lua = (
        'KezanAHDB = {\n'
        '  lastScan = 1723202123,\n'
        '  realm = "Sanguino",\n'
        '  faction = "Alliance",\n'
        '  items = { [19019] = { price = 123456, qty = 2, seller = "Goblin", ts = 1723202123 }, },\n'
        '  playerStats = { multicraft = 0.27, resourcefulness = 0.12, inspiration = 0.18, craftingSpeed = 0.22, skill = 211 }\n'
        '}\n'
    )
    out = parse_savedvariables(lua)
    assert out["lastScan"] == 1723202123
    assert out["realm"] == "Sanguino"
    assert out["items"][19019]["price"] == 123456
    assert out["playerStats"]["multicraft"] == 0.27


def test_cloud_history_roundtrip(tmp_path):
    store = {}

    def downloader(key):
        return store.get(key)

    def uploader(key, data):
        store[key] = data

    client = CloudHistoryClient(downloader=downloader, uploader=uploader)
    key = client.build_key("eu", "sanguino", "2025-08-09T10")
    payload = {"ok": True, "n": 1}
    assert client.upload_snapshot(key, payload) is True
    loaded = client.download_snapshot(key)
    assert loaded == payload
