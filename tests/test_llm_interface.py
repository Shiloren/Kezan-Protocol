"""Pruebas para la interfaz del LLM local."""

import httpx
import pytest

from kezan import llm_interface


class Resp:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_analyze_items_with_llm(monkeypatch):
    """Retorna texto cuando la respuesta es válida."""
    monkeypatch.setattr(httpx, "post", lambda *a, **k: Resp({"response": "ok"}))
    res = llm_interface.analyze_items_with_llm([{"a": 1}])
    assert res == "ok"


def test_analyze_items_with_llm_empty(monkeypatch):
    """Error cuando el modelo responde vacío."""
    monkeypatch.setattr(httpx, "post", lambda *a, **k: Resp({"response": ""}))
    with pytest.raises(RuntimeError):
        llm_interface.analyze_items_with_llm([{}])


def test_analyze_items_with_llm_error(monkeypatch):
    """Lanza error si la solicitud falla."""
    def fake_post(*a, **k):
        raise httpx.HTTPError("fail")

    monkeypatch.setattr(httpx, "post", fake_post)
    with pytest.raises(RuntimeError):
        llm_interface.analyze_items_with_llm([])


def test_analyze_recipes_with_llm(monkeypatch):
    """Analiza recetas incluyendo inventario previo."""
    monkeypatch.setattr(httpx, "post", lambda *a, **k: Resp({"response": "texto"}))
    res = llm_interface.analyze_recipes_with_llm([{"r": 1}], inventory=[1])
    assert res == "texto"


def test_analyze_recipes_with_llm_error(monkeypatch):
    """Lanza error si el LLM no responde."""
    def boom(*a, **k):
        raise httpx.HTTPError("fail")

    monkeypatch.setattr(httpx, "post", boom)
    with pytest.raises(RuntimeError):
        llm_interface.analyze_recipes_with_llm([])


def test_analyze_recipes_with_llm_empty(monkeypatch):
    """Error cuando la respuesta de recetas está vacía."""
    monkeypatch.setattr(httpx, "post", lambda *a, **k: Resp({"response": ""}))
    with pytest.raises(RuntimeError):
        llm_interface.analyze_recipes_with_llm([{}])
