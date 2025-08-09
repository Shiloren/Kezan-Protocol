# Prompt maestro para Copilot – Proyecto Kezan Protocol

## Visión
Kezan Protocol es una herramienta de optimización económica para World of Warcraft que aspira a convertirse en el sucesor de TradeSkillMaster (TSM), superándolo en funcionalidad, facilidad de uso y capacidad de análisis inteligente. No pretende ser un clon, sino una evolución con un enfoque moderno, centrado en IA, predicción avanzada y experiencia de usuario simplificada.

---

## 1. Filosofía del proyecto
- Cumplimiento total de los Términos de Servicio de Blizzard.
- Procesamiento y análisis siempre fuera del cliente de WoW.
- Enfoque plug & play: la aplicación final debe instalarse fácilmente, traer integrado el entorno de simulación de IA y todas las conexiones necesarias, y solo requerir la API key oficial de Blizzard para empezar a funcionar.
- Acceso opcional desde dentro del juego mediante addon que permita, entre otras cosas, interactuar con el chat de la IA.

### Guardarraíles de cumplimiento (Blizzard‑safe)
- Principio 1: “Sólo lectura/asesoría”. La app nunca manda inputs al cliente de WoW.
- Principio 2: Addon informativo: muestra datos, chat IA, reglas y pasos; no ejecuta acciones.
- Principio 3: Telemetría opt‑in, logs claros y auditables para demostrar uso legítimo.
- Principio 4: Botón “Abrir en Casa de Subastas” (navega, no actúa). Todo clic lo hace el jugador.

---

## 2. Arquitectura general

### Componentes principales:

1. **Addon LUA in-game**
   - Muestra recomendaciones, métricas y chat IA directamente dentro de WoW.
   - Permite consultar reglas, simulaciones y oportunidades sin salir del juego.

2. **Aplicación principal (desktop/web)**
   - Configuración inicial y almacenamiento de credenciales/API keys.
   - Motor de ingesta de datos desde Blizzard API y de logs de subasta.
   - Entorno de simulación integrado para probar estrategias y modelos.

3. **Backend local o en la nube**
   - Ingesta: datos de subastas, recetas, profesiones, históricos y realm data.
   - Procesamiento: filtrado determinista, detección de anomalías, scoring ML.
   - Motor IA: análisis predictivo, generación de reglas, explicaciones, ajustes automáticos de estrategias.

4. **Cliente móvil/PWA (opcional)**
   - Alertas push, panel de oportunidades y craft planner.

---

## 3. Flujo de trabajo en cascada (optimización de IA)
- T0 – Filtros rápidos: criterios básicos (precio vs. P50, rotación mínima, margen objetivo).
- T1 – Ranking ML: modelos ligeros para detección de gangas y estimación de beneficios.
- T2 – Reranking contextual: embeddings para información externa relevante (parches, foros, etc.).
- T3 – LLM (local): recibe solo el Top-N de candidatos y devuelve explicación, reglas DSL y plan de salida.

---

## 4. Entorno de simulación
- Incluido de serie en la instalación.
- Permite reproducir mercados históricos y simular comportamientos de agentes (jugadores, undercutters, competidores agresivos).
- Facilita probar estrategias y medir métricas como ROI, tiempo hasta venta o volatilidad antes de aplicarlas en el juego real.

---

## 5. Diferenciadores clave respecto a TSM
1. IA adaptativa que aprende de las decisiones y resultados del propio usuario.
2. Simulador interno para validar estrategias sin riesgo real.
3. Interfaz de reglas en lenguaje natural → conversión automática a DSL interna.
4. Alertas claras con explicación breve y pasos sugeridos.
5. Chat IA accesible desde el addon de WoW.

---

## 6. Datos y features clave
- Históricos de precios y volúmenes por ítem/reino.
- Costes de crafteo dinámicos con sustitutos y subproductos.
- Métricas de volatilidad, momentum, elasticidad y rotación.
- Detección de anomalías basada en mediana y dispersión.
- Oportunidades de arbitraje entre reinos y calidades.

---

## 7. Tecnologías recomendadas
- Backend: Python, FastAPI, TimescaleDB, Redis, S3/Parquet, Ray.
- ML: scikit-learn, LightGBM, PyOD, OR-Tools.
- LLM local: Ollama, vLLM, llama.cpp.
- Embeddings: e5-small-v2, bge-small.
- Frontend: LUA addon, Electron/PyQt, PWA.
- Infra: Docker/K8s, GitHub Actions.

---

## 8. Interacción con la IA
- Entrada (JSON): resumen de métricas clave por ítem.
- Salida (JSON, sólo asesoría): recomendaciones (tipo, parámetros sugeridos), explicación breve, regla DSL generada, riesgos asociados. La IA nunca controla el cliente; puede sugerir acciones y proveer ayudas de UX (p. ej., preparar búsquedas o cadenas para copiar).

---

## Instrucción para Copilot
> Guarda este documento como `docs/kezan_protocol_master_prompt.md`.
>
> Utiliza este archivo como contexto persistente en todo el desarrollo de Kezan Protocol.
>
> Asegúrate de que cada nueva función o módulo siga las directrices aquí descritas, manteniendo el enfoque plug & play y la integración del entorno de simulación.
>
> Cualquier nueva información relevante debe añadirse a este documento y versionarse.

---

## 9. DSL de reglas (versión inicial)

Esta sección define una mini‑gramática declarativa para expresar reglas de trading, crafteo y gestión de riesgo en Kezan Protocol. Debe ser fácil de parsear y estable en el tiempo; las extensiones deben mantener compatibilidad retroactiva.

### 9.1 Mini‑gramática (modo asesor)

Bloques de regla:

```
RULE "<nombre>"
WHEN <condición booleana>
THEN <acciones separadas por ;>
WITH <clave=valor, ...>
```

- Operadores: `>`, `>=`, `<`, `<=`, `==`, `!=`, `AND`, `OR`, `NOT`, `BETWEEN`.
- Helpers: `FLOOR()`, `CEIL()`, `MIN()`, `MAX()`, `ABS()`, `EMA()`, `ZSCORE()`, `MAD()`, `MEDIAN()`, `EXISTS()`.
- Acciones permitidas (asesoría): `RECOMMEND_BUY(qty,target,eta_h)`, `RECOMMEND_CRAFT(qty,target,eta_h)`, `SET(key,value)` (sólo estado interno del motor), `ALERT(type,msg)`, `WATCHLIST(tag)`, `SIMULATE(days,strategy)`, `SKIP(reason)`, `NOTIFY(channel)`, `OPEN_AH_SEARCH(query)`, `COPY_POST_STRING(text)`.
- Acciones prohibidas (no conformes): `BUY`, `CRAFT`, `CANCEL`, `POST`, `REPOST`, `UNDERCUT`, `AUTOBUY`, `AUTOCRAFT`, y similares.
- Metadatos opcionales (cláusula `WITH`): `PRIORITY=...`, `COOL_DOWN="6h"`, `WINDOW="48h"`, `ENABLED=true`, etc.
- Notación de propiedades anidadas: `obj.attr` (p.ej., `substitute.eff_cost`).

### 9.2 Variables comunes (inputs del motor)

`price`, `p50_7d`, `p50_30d`, `vol_7d`, `rot` (ventas/día), `spread` (bid‑ask %), `pred_72h` (predicción), `risk` (0–1), `craft_cost`, `roi` (beneficio/coste), `capital`, `stock` (inventario), `listings` (# anuncios), `undercut_rate`, `quality` (rango/calidad), `region_vol`, `connected_realm_spread`, `days_on_market`, `fee` (comisión), `is_commodity` (bool), `MAD_7d`.

Objetos/aliases contextuales: `ingredient`, `substitute` (permiten acceso por `.` a sub‑campos como `eff_cost`).

### 9.3 Reglas base (útiles desde el día 1, modo asesor)

```
1) Ganga commodity sólida (flip rápido)
RULE "flip_commodity_descuento_fuerte"
WHEN is_commodity AND price < p50_30d*0.75 AND vol_7d > 800 AND rot >= 0.8
THEN
   RECOMMEND_BUY(qty=FLOOR( MIN(capital*0.12, 200000) / price ),
         target=p50_7d*0.98, eta_h=36);
   ALERT("flip","Descuento >25% vs P50_30d con buena rotación");
   OPEN_AH_SEARCH(query="item:{{item_id}}")
WITH PRIORITY=90, WINDOW="48h", COOL_DOWN="2h"

2) No‑commodity poco listado (escasez + descuento)
RULE "flip_raro_baja_competencia"
WHEN NOT is_commodity AND price < p50_30d*0.70 AND listings <= 3 AND vol_7d >= 40
THEN
      RECOMMEND_BUY(qty=MIN(3, FLOOR(capital*0.08/price)),
         target=MAX(p50_7d*0.97, p50_30d*0.9), eta_h=48);
   ALERT("flip","Pocas unidades listadas, rebote probable")
WITH PRIORITY=85, WINDOW="72h"

3) Evitar pozos de liquidez
RULE "antipozo_liquidez"
WHEN vol_7d < 30 OR rot < 0.3
THEN SKIP("Liquidez insuficiente para venta <72h")
WITH PRIORITY=100

4) Stop‑loss/ajuste tras 3 días sin vender
RULE "ajuste_precio_lento"
WHEN days_on_market >= 3 AND undercut_rate > 0.6
THEN
   SET("new_price", MAX(p50_7d*0.97, price*0.98));
   ALERT("pricing","Repostear con ajuste prudente")
WITH PRIORITY=70, COOL_DOWN="12h"

5) Límite de exposición por ítem
RULE "control_riesgo_por_item"
WHEN TRUE
THEN SET("max_alloc_per_item", capital*0.15); SET("max_units", 50)
WITH PRIORITY=60

6) Flip por momentum + predicción
RULE "flip_momentum_pred"
WHEN ZSCORE(price, p50_7d, MAD_7d) < -1.2 AND pred_72h >= p50_7d
THEN
      RECOMMEND_BUY(qty=FLOOR( MIN(capital*0.10, 150000) / price ),
         target=MIN(pred_72h*0.99, p50_7d*1.01), eta_h=30);
   ALERT("flip","Precio bajo anómalo con predicción favorable")
WITH PRIORITY=92

7) Craft rentable (consumible top)
RULE "craft_consumible_rentable"
WHEN craft_cost > 0 AND p50_7d > 0 AND (p50_7d - craft_cost - fee) / craft_cost >= 0.25 AND rot >= 0.8
THEN
      RECOMMEND_CRAFT(qty=MIN( CEIL(capital*0.12/craft_cost), 100), target=p50_7d*0.99, eta_h=36);
   ALERT("craft","ROI ≥25% y rotación alta")
WITH PRIORITY=88, WINDOW="48h"

8) Sustitución de ingredientes (ahorro equivalente)
RULE "sustitutos_BOM"
WHEN EXISTS(substitute) AND substitute.eff_cost < ingredient.eff_cost*0.9
THEN SET("use_substitute", true)
WITH PRIORITY=65

9) Vendor shuffle obvio
RULE "vendor_arbitrage_simple"
WHEN vendor_price > price*1.08 AND vol_7d >= 200
THEN RECOMMEND_BUY(qty=FLOOR( MIN(capital*0.05, 50000) / price ));
WITH PRIORITY=55

10) Arbitraje en connected realm (informativo)
RULE "arbitraje_connected_realms_info"
WHEN connected_realm_spread >= 0.20 AND NOT is_commodity
THEN ALERT("info","Spread ≥20% entre connected realms; considera transferencia manual")
WITH PRIORITY=40

11) Evitar sobre‑stock
RULE "cap_inventario"
WHEN stock >= 50 OR stock*price >= capital*0.25
THEN SKIP("Demasiado capital inmovilizado en este ítem")
WITH PRIORITY=95

12) Entrada conservadora en parches
RULE "parche_volatil_precaucion"
WHEN spread > 0.15 AND rot < 0.6
THEN SKIP("Mercado volátil/ilíquido tras parche")
WITH PRIORITY=80

13) Cancel‑repost inteligente (margen vs. coste)
RULE "cancel_repost_heuristica"
WHEN undercut_rate >= 0.5 AND (p50_7d - price) / p50_7d <= 0.03
THEN ALERT("pricing","Repostear si coste<beneficio esperado a 24h (manual)")
WITH PRIORITY=50, COOL_DOWN="6h"

14) Lista de vigilancia (alto potencial, baja señal)
RULE "watchlist_potencial"
WHEN price < p50_30d*0.85 AND vol_7d BETWEEN 80 AND 200 AND rot BETWEEN 0.5 AND 0.8
THEN WATCHLIST("observacion_48h")
WITH PRIORITY=45

15) Bucket de riesgo (asigna perfil)
RULE "perfil_riesgo_bucket"
WHEN roi >= 0.35 AND rot >= 1.0
THEN SET("risk_bucket","ALTO")
WHEN roi BETWEEN 0.20 AND 0.35 AND rot >= 0.7
THEN SET("risk_bucket","MEDIO")
ELSE SET("risk_bucket","BAJO")
WITH PRIORITY=50

16) Top‑N a LLM (solo lo mejor de lo mejor)
RULE "llm_gate_topN"
WHEN roi >= 0.30 AND rot >= 0.8 AND price >= 200
THEN NOTIFY("LLM_QUEUE"); ALERT("analysis","Enviar a IA para explicación/regla DSL")
WITH PRIORITY=89, COOL_DOWN="1h"

17) Simular antes de habilitar regla nueva
RULE "simular_antes_de_activar"
WHEN TRUE
THEN SIMULATE(days=14, strategy="actual + regla_nueva");
   ALERT("sim","Backtest 14d requerido antes de ENABLED=true (asesoría)")
WITH PRIORITY=100, ENABLED=false

18) Protección contra fees
RULE "proteccion_fees"
WHEN (fee / MAX(price,1)) > 0.05 AND rot < 0.6
THEN SKIP("Fee elevado y salida lenta; riesgo de sangrado por cancelaciones")
WITH PRIORITY=75

19) Salida escalonada (ladder)
RULE "venta_escalonada"
WHEN stock >= 10 AND rot >= 1.0
THEN SET("ladder","3 tramos: 40%@p50_7d*1.01; 40%@p50_7d; 20%@p50_7d*0.98")
WITH PRIORITY=58

20) Hard cap por ítem “caliente”
RULE "hardcap_item_caliente"
WHEN roi >= 0.50 AND vol_7d >= 1000
THEN SET("hard_cap_units", 200); SET("hard_cap_alloc", capital*0.20)
WITH PRIORITY=76
```

### 9.4 Ejemplo de salida JSON (referencia IA)

```json
{
   "actions": [
      {
         "item": 19019,
         "type": "RECOMMEND_BUY",
         "buy_qty": 12,
         "target_sell": 30000,
         "eta_h": 36,
         "why": "Descuento 28% vs P50_30d, rotación 0.9/d, volatilidad moderada",
         "rule": "WHEN price < P50_30d*0.75 AND rot>0.7 THEN RECOMMEND_BUY(12,target=P50_7d*0.98)"
      }
   ],
   "risks": [
      "Undercut agresivo nocturno",
      "Subida de oferta post‑parche"
   ]
}
```

### 9.5 UX del addon (seguro)
- Panel “Hoy, haz esto”: lista de recomendaciones con por qué, cómo y botones: Abrir AH / Copiar precio.
- Chat IA in‑game: preguntas/respuestas, siempre asesoría.
- Indicadores de cumplimiento: “⚖️ Modo asesor” en todo momento.
