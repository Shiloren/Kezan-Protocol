"""Prueba de integración de la GUI (omitida sin entorno gráfico)."""

import os
import pytest

tk = pytest.importorskip("tkinter")

if not os.environ.get("DISPLAY"):
    pytest.skip("Sin entorno gráfico disponible", allow_module_level=True)


def test_dummy_gui():
    """La prueba pasa si se puede crear una ventana básica."""

    root = tk.Tk()
    root.withdraw()
    root.destroy()

