"""Cliente simple para histórico en la nube (upload/download).

Este módulo define una interfaz mínima. La implementación real dependerá de la
plataforma (R2/S3/KV/HTTP). Aquí se dejan stubs y validaciones básicas.
"""
from __future__ import annotations

import gzip
import io
import json
from typing import Optional


class CloudHistoryClient:
    def __init__(self, downloader=None, uploader=None):
        self.downloader = downloader  # Callable(key) -> bytes
        self.uploader = uploader      # Callable(key, bytes) -> None

    @staticmethod
    def build_key(region: str, realm: str, timestamp_iso_hour: str) -> str:
        return f"{region}:{realm}:{timestamp_iso_hour}.json.gz"

    def download_snapshot(self, key: str) -> Optional[dict]:
        if not self.downloader:
            return None
        data = self.downloader(key)
        if not data:
            return None
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data), mode="rb") as f:
                return json.loads(f.read().decode("utf-8"))
        except Exception:
            return None

    def upload_snapshot(self, key: str, payload: dict) -> bool:
        if not self.uploader:
            return False
        try:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as f:
                f.write(json.dumps(payload).encode("utf-8"))
            self.uploader(key, buf.getvalue())
            return True
        except Exception:
            return False
