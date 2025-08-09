# Detección de “ganga” en subastas (Blizzard API)

Este documento resume el módulo `kezan/bargain_detector.py` que etiqueta oportunidades como "ganga" a partir de snapshots de la API de Blizzard.

## Entradas
- Commodities: `GET /data/wow/auctions/commodities` → `item.id`, `quantity`, `unit_price`.
- No‑commodities: `GET /data/wow/connected-realm/{id}/auctions` → `item.id`, `quantity`, `buyout`, `bid`, `time_left`.

Normalización por unidad:
- Commodity: `price_u = unit_price`.
- No‑commodity: si `buyout` existe → `price_u = buyout / max(quantity,1)`; si no, descartar.

Claves para históricos:
- Commodities: `(region, item_id, quality?)`.
- No‑commodities: `(connected_realm_id, item_id, quality?)`.

## Features mínimas
- `P50_7d`, `P50_30d`, `MAD_7d`, `vol_7d`, `rot`, `volatilidad_7d` (opcional), `pred_72h` (opcional).

## Candidatos
- `discount_flag = price_u <= 0.75*P50_30d AND price_u <= 0.85*P50_7d`.
- `zscore` con MAD robusto: `z = (price_u - P50_7d) / (1.4826*max(MAD_7d, eps))`.
- `candidate = discount_flag OR (z <= -1.5)`.
- `liquidity_ok`: commodities `vol_7d >= 200`; no‑commodities `vol_7d >= 40`.

## Scoring y decisión
- Heurístico inicial `rule_score` (sustituible por ML): combina `rel_7d`, `rel_30d` y `rot`.
- `is_bargain` si `candidate AND liquidity_ok AND score >= 0.6`.

## Salida (sólo asesoría)
- `recommendation_type = "RECOMMEND_BUY"` y `qty_sugerida` basada en capital y precio_u.
- `target_sell` heurístico y `eta_h` estimado.

## Pruebas
- `tests/test_bargain_detector.py` incluye unit tests para normalización, zscore y filtros.
