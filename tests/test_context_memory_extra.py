"""Pruebas adicionales para el manejo de contexto."""

from kezan import context_memory


def test_clean_missing_and_invalid_timestamp(monkeypatch):
    """_clean debe mantener entradas sin o con timestamp inválido."""
    datos = [{"msg": "a"}, {"timestamp": "no-es-fecha"}]
    resultado = context_memory._clean(datos)
    assert len(resultado) == 2


def test_load_context_bad_json(tmp_path):
    """Carga segura cuando el archivo contiene JSON corrupto."""
    archivo = tmp_path / "ctx.json"
    archivo.write_text("{")
    assert context_memory.load_context(str(archivo)) == []


def test_load_context_from_csv_invalid_rows(tmp_path):
    """Ignora filas inválidas en CSV y no crea archivo si ninguna es válida."""
    csv_path = tmp_path / "datos.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        fh.write("timestamp,valor\ninvalid,1\n")
    dest = tmp_path / "ctx.json"
    context_memory.load_context_from_csv(str(csv_path), str(dest))
    assert not dest.exists()
