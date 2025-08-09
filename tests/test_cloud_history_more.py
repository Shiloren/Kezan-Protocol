import gzip
import io
import json

from kezan.cloud_history import CloudHistoryClient


def test_download_snapshot_no_downloader_returns_none():
    c = CloudHistoryClient()
    assert c.download_snapshot("k") is None


def test_download_snapshot_invalid_gzip_returns_none():
    def downloader(_k):
        return b"not-gzip"
    c = CloudHistoryClient(downloader=downloader)
    assert c.download_snapshot("k") is None


def test_upload_snapshot_no_uploader_returns_false():
    c = CloudHistoryClient()
    assert c.upload_snapshot("k", {"a": 1}) is False


def test_upload_snapshot_uploader_exception_returns_false():
    def uploader(_k, _b):
        raise RuntimeError("boom")
    c = CloudHistoryClient(uploader=uploader)
    assert c.upload_snapshot("k", {"a": 1}) is False


def test_build_key_format():
    key = CloudHistoryClient.build_key("eu", "sanguino", "2025-08-09T12")
    assert key.startswith("eu:sanguino:") and key.endswith(".json.gz")
from kezan.cloud_history import CloudHistoryClient


def test_cloud_history_no_handlers_and_corrupt():
    # No handlers present
    client = CloudHistoryClient()
    assert client.download_snapshot("eu:sanguino:2025-08-09T10.json.gz") is None
    assert client.upload_snapshot("k", {"x": 1}) is False

    # Corrupt data path
    store = {"eu:a:2025-08-09T10.json.gz": b"not-gzip"}

    def downloader(key):
        return store.get(key)

    client2 = CloudHistoryClient(downloader=downloader)
    assert client2.download_snapshot("eu:a:2025-08-09T10.json.gz") is None


def test_build_key_format():
    key = CloudHistoryClient.build_key("eu", "sanguino", "2025-08-09T10")
    assert key.endswith(".json.gz") and key.startswith("eu:sanguino:")
