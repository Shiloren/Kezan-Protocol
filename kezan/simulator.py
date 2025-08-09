"""Simulador mínimo (v1) para backtests de reglas/estrategias.

Este módulo ofrece una interfaz simple para simular resultados sobre datos históricos
disponibles (cuando existan), devolviendo métricas básicas.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SimulationResult:
    roi: float
    volatility: float
    est_time_to_sell_h: float
    trades: int
    notes: str


def run_backtest(strategy: Dict[str, Any], history: List[Dict[str, Any]] | None = None) -> SimulationResult:
    """Backtest mínimo placeholder.

    - strategy: dict con descripción/parametros de la estrategia o regla DSL.
    - history: lista de snapshots/históricos (opcional). Si no hay datos, devuelve métricas neutras.
    """
    if not history:
        return SimulationResult(roi=0.0, volatility=0.0, est_time_to_sell_h=48.0, trades=0, notes="No history; neutral baseline")

    # Placeholder: computar métricas simples en base a recuentos y dispersiones sintéticas
    trades = min(len(history), 100)
    roi = 0.10  # 10% como valor por defecto hasta tener motor real
    volatility = 0.20
    est_time_to_sell_h = 36.0
    return SimulationResult(roi=roi, volatility=volatility, est_time_to_sell_h=est_time_to_sell_h, trades=trades, notes="Prototype")
