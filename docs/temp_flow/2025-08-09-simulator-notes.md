# 2025-08-09: Notas de diseño del Simulador v1

- Objetivo: backtests con ≥14 días de histórico; métricas ROI, volatilidad, tiempo estimado de venta.
- v1 (placeholder) devuelve baseline si no hay históricos; integración con `cloud_history` prevista.
- Próximos pasos:
  - Cargar `*.json.gz` recientes (por realm) y mapear a series por item.
  - Ejecutar reglas DSL sobre los snapshots (modo asesoría-only, sin acciones ejecutivas).
  - Calcular métricas y persistir un informe ligero (CSV/JSON) en `.cache/sim/`.
