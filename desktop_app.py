"""Simple desktop interface for the Kezan Protocol analysis service."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
import os
import tkinter as tk
from tkinter import ttk

import httpx

from kezan.initializer import ensure_credentials
from kezan.logger import get_logger

try:
    _root = tk.Tk()
    _root.withdraw()
    _root.update()
    _root.destroy()
except tk.TclError:
    logger = get_logger(__name__)
    logger.error(
        "No se detectó entorno gráfico. Ejecuta esta app en un PC con escritorio."
    )
    sys.exit(1)

# Ensure Blizzard API credentials are present before launching the app
if not ensure_credentials(use_gui=True):
    sys.exit(1)

logger = get_logger(__name__)

API_URL = "http://localhost:8000/api/consejo"
HISTORY_FILE = Path(os.path.expanduser("~/.kezan/history.json"))


class KezanApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Kezan Protocol")
        self.geometry("700x500")

        self._build_widgets()
        self.history = self._load_history()
        for entry in self.history:
            self.history_list.insert(tk.END, f"{entry['timestamp']}: {entry['recomendacion'][:30]}...")

    def _build_widgets(self) -> None:
        filters = ttk.Frame(self)
        filters.pack(fill="x", padx=5, pady=5)

        ttk.Label(filters, text="Limit:").pack(side="left")
        self.limit_var = tk.StringVar(value="5")
        ttk.Entry(filters, textvariable=self.limit_var, width=5).pack(side="left", padx=(0, 5))

        ttk.Label(filters, text="Min Margin:").pack(side="left")
        self.margin_var = tk.StringVar(value="0.3")
        ttk.Entry(filters, textvariable=self.margin_var, width=5).pack(side="left", padx=(0, 5))

        ttk.Button(filters, text="Actualizar Datos", command=self.fetch_data).pack(side="left")

        # Items table
        columns = ("name", "ah_price", "avg_sell_price", "margin")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("name", text="Item")
        self.tree.heading("ah_price", text="AH Price")
        self.tree.heading("avg_sell_price", text="Avg Sell")
        self.tree.heading("margin", text="Margin")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Label(self, text="Análisis de la IA:").pack(anchor="w", padx=5)
        self.analysis_text = tk.Text(self, height=6)
        self.analysis_text.pack(fill="x", padx=5, pady=5)

        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var).pack(fill="x", padx=5, pady=(0,5))

        ttk.Label(self, text="Historial:").pack(anchor="w", padx=5)
        self.history_list = tk.Listbox(self, height=5)
        self.history_list.pack(fill="both", expand=True, padx=5, pady=5)

    def _load_history(self):
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text())
            except Exception:
                return []
        return []

    def _save_history(self) -> None:
        try:
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            HISTORY_FILE.write_text(json.dumps(self.history, indent=2))
        except IOError as exc:
            logger.error("No se pudo guardar historial: %s", exc)

    def fetch_data(self) -> None:
        params = {"limit": self.limit_var.get(), "min_margin": self.margin_var.get()}
        try:
            resp = httpx.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # network or HTTP error
            logger.error("No se pudo obtener datos: %s", exc)
            self.status_var.set(f"Error al obtener datos: {exc}")
            return

        self.tree.delete(*self.tree.get_children())
        for item in data.get("items", []):
            self.tree.insert("", tk.END, values=(
                item.get("name"),
                item.get("ah_price"),
                item.get("avg_sell_price"),
                item.get("estimated_margin"),
            ))

        if "error" in data:
            logger.error("Error de la API: %s", data["error"])
            self.status_var.set(data["error"])

        recomendacion = data.get("recomendacion", "")
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, recomendacion)

        if recomendacion:
            entry = {"timestamp": datetime.now().isoformat(timespec="seconds"), "recomendacion": recomendacion}
            self.history.append(entry)
            self.history_list.insert(tk.END, f"{entry['timestamp']}: {recomendacion[:30]}...")
            self._save_history()
            self.status_var.set("Datos actualizados correctamente")


if __name__ == "__main__":
    app = KezanApp()
    app.mainloop()
