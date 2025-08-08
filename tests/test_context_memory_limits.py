"""Pruebas para el límite de memoria de contexto."""

from kezan import context_memory


def test_context_prunes_old_entries(tmp_path, monkeypatch):
    """Verifica que solo se conserven las últimas entradas según CTX_MAX_ENTRIES."""

    monkeypatch.setenv("CTX_MAX_ENTRIES", "2")
    path = tmp_path / "ctx.json"

    for i in range(3):
        context_memory.append_context({"msg": i}, path)

    data = context_memory.load_context(path)
    assert len(data) == 2
    assert data[0]["msg"] == 1 and data[1]["msg"] == 2

