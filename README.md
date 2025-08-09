# 🧠 Kezan Protocol

## Índice
- [Introducción](#introducción)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración inicial](#configuración-inicial)
- [Ejecución](#ejecución)
  - [API HTTP](#api-http)
  - [Interfaz de escritorio](#interfaz-de-escritorio)
- [Flujo de datos paso a paso](#flujo-de-datos-paso-a-paso)
- [Módulos principales](#módulos-principales)
- [Pruebas](#pruebas)
- [Errores comunes](#errores-comunes)
 - [Guía maestra del proyecto](#guía-maestra-del-proyecto)
 - [Documentación y build de docs](#documentación-y-build-de-docs)

---

## Introducción
Kezan Protocol es una herramienta diseñada para analizar mercados virtuales en el universo de World of Warcraft (WoW). Inspirada en los goblins de Kezan, esta aplicación combina tecnología avanzada con un enfoque en maximizar ganancias virtuales. Ofrece una interfaz de usuario moderna y funcional, junto con una API REST para integraciones avanzadas.

---

## Arquitectura

Tres piezas trabajan juntas para optimizar el comercio en WoW:

1) Addon Kezan Protocol (WoW)
   - Escaneo de AH (full o selectivo) y captura de stats de crafteo (multicraft, resourcefulness, inspiration, craftingSpeed, skill y reagentes).
   - Guarda en SavedVariables con estructura compacta. Ver `docs/addon-spec.md`.

2) Bot de históricos en la nube
   - Cada hora descarga `/data/wow/connected-realm/{id}/auctions` y opcionalmente `/data/wow/auctions/commodities`.
   - Guarda snapshots comprimidos por clave `region:realm:YYYY-MM-DDTHH.json.gz`. Ver `docs/bot-spec.md`.

3) Cliente Kezan Protocol (PC)
   - Lee SavedVariables del addon y descarga el snapshot más reciente del bot.
   - Cruza datos locales vs globales, aplica ML ligero y valida top-N con IA local (Llama 3 8B Instruct cuantizado).

Diagrama de flujo (conceptual): Addon ↔ Cliente PC ↔ Bot/API Blizzard, con rutas gratis y Premium diferenciadas. Ver `docs/integration-guide.md`.

---

## Requisitos
- Backend: Python 3.10+ (recomendado 3.12)
- Frontend (opcional para UI): Node.js 18+ y npm 9+
- Dependencias: Ver `requirements.txt` y `frontend/package.json`.

### Requisitos del sistema (mínimos y recomendados)
- CPU: 4 núcleos x86_64 (mínimo); 8+ núcleos recomendado si se usa IA local.
- RAM: 8 GB (mínimo); 16 GB recomendado para LLMs ligeros (3-8B). Para modelos >8B, 24-32 GB.
- Almacenamiento: 2 GB libres (logs, cache, docs). Para IA local con varios modelos, 10-30 GB.
- GPU (opcional): Para acelerar LLM locales. 6 GB VRAM (mínimo práctico para 7B cuantizado); 12+ GB recomendado.
- SO: Windows 10/11, macOS 13+, o Linux x86_64.

Notas IA:
- Ollama con modelos 7B cuantizados (q4_0/q5_0) funciona en CPU; GPU acelera notablemente.
- LM Studio (OpenAI-style) también es compatible. Configura `LLM_API_URL` y `LLM_API_KEY` si aplica.

---

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Shiloren/Kezan-Protocol.git
   cd Kezan-Protocol
   ```

2. Instala las dependencias del backend:
   ```bash
   pip install -r requirements.txt
   ```

3. Instala las dependencias del frontend:
   ```bash
   cd frontend
   npm install
   ```

---

## Configuración inicial

1. Crea un archivo `.env` basado en `example.env`.
2. Configura las credenciales de la API de Blizzard (se aceptan ambos prefijos):
   - `BLIZZ_CLIENT_ID` o `BLIZZARD_CLIENT_ID`
   - `BLIZZ_CLIENT_SECRET` o `BLIZZARD_CLIENT_SECRET`
   - `REGION` (ej. `eu`, `us`)
   - `REALM_ID` (connected realm ID)
3. (Opcional) Configura IA local:
   - Variables: `LLM_API_URL` (por defecto `http://localhost:11434/api/generate`), `LLM_MODEL`, `LLM_API_KEY` (si usas OpenAI-style).
   - Plantillas de modelo en `templates/*.json` (usa `load_model_template(nombre)` para aplicarlas).

---

## Ejecución

### API HTTP
Ejecuta el backend con FastAPI (ASGI) usando Uvicorn:

```powershell
# Entorno virtual recomendado (Windows PowerShell)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Levantar la API en http://127.0.0.1:8000
python -m pip install uvicorn
uvicorn main:app --reload
```

Endpoints nuevos (básicos):
- POST `/api/simulate` → backtest mínimo del simulador v1 (placeholder seguro)
- GET `/api/premium-check` → plan actual (placeholder: Free/Pro según api_key)

### Interfaz de escritorio
Ejecuta la aplicación Tauri:
```powershell
cd frontend
npm install
npm run dev:tauri
```

---

## Flujo de datos paso a paso
1. El usuario inicia la aplicación.
2. `blizzard_api` obtiene datos de subastas.
3. `analyzer` y `crafting_analyzer` procesan los datos.
4. `llm_interface` genera recomendaciones en modo asesoría, aplicando `advisory_preamble` y `sanitize_dsl_text` para garantizar acciones permitidas (RECOMMEND_*, OPEN_AH_SEARCH, COPY_POST_STRING, etc.).
5. Los resultados se muestran en la interfaz o se exponen vía API.

---

## Módulos principales
- **`blizzard_api`**: Gestión OAuth y descarga de datos (subastas, commodities).
- **`analyzer`**: Agregados y top-N de oportunidades.
- **`crafting_analyzer`**: Evaluación de recetas y costes efectivos.
- **`auction_analyzer`**: Escaneos y alertas por umbrales (watched items).
- **`realtime_monitor`**: Monitor en tiempo real y snapshots de mercado.
- **`llm_interface`**: Integración con LLM (Ollama y OpenAI-style) con guardarraíles Blizzard-safe.
- **`market_optimizer`**: Preprocesado (requiere NumPy si se usa en runtime).
- **`cloud_history`**: Carga/descarga de snapshots comprimidos (gzip JSON).
- **`sv_parser`**: Parseo de SavedVariables del addon.
- **`frontend/`**: Interfaz Tauri/React.

---

## Pruebas y cobertura
Ejecuta las pruebas unitarias y genera cobertura en terminal:
```powershell
pytest -q --disable-warnings --cov=kezan --cov-report=term-missing
```

Para reporte HTML:
```powershell
if (Test-Path htmlcov) { Remove-Item htmlcov -Recurse -Force }
pytest -q --disable-warnings --cov=kezan --cov-report=html
```

Estado actual de cobertura: ~92% (objetivo ≥95%).

Áreas cubiertas por tests recientes:
- `llm_interface`: ramas de errores (HTTP/JSON), prompts con inventario, sanitización DSL.
- `realtime_monitor`: timestamps y age_seconds en snapshots.
- `auction_analyzer`: alertas por umbral en watched items.
- `cloud_history`: paths de fallo en gzip/JSON/ausencia de backend.
- `market_optimizer`: shim de NumPy para preprocesado y rama de error.

### Análisis estático
```powershell
ruff check .
black --check .
```

### Dependencias
- Python:
   ```powershell
   pip list --outdated
   pip install pip-audit; pip-audit -r requirements.txt
   ```
- Frontend:
   ```powershell
   npm outdated
   npm audit
   ```

---

## Errores comunes
1. **Error de credenciales**:
   - Asegúrate de configurar correctamente el archivo `.env`.

2. **Problemas con dependencias**:
   - Verifica que las versiones de Python y Node.js sean compatibles.

3. **NumPy no instalado**:
   - El módulo `market_optimizer` importa NumPy. Si vas a usar preprocesado avanzado en runtime, instala `numpy`:
   ```powershell
   python -m pip install numpy
   ```
   (Las pruebas usan un shim para evitar dependencia dura.)

---

## Guía maestra del proyecto
Para la visión, arquitectura, DSL de asesoría y guardarraíles Blizzard-safe, consulta:

- docs/kezan_protocol_master_prompt.md

Toda nueva funcionalidad debe alinearse con esta guía. Si surgen decisiones de arquitectura o criterios adicionales, añade esa información al documento y versiona el cambio.

---

## Roadmap
El roadmap detallado y fuente de verdad está en:
- docs/ROADMAP.md

Nota: El Prompt Maestro incluye un snapshot resumido para dar contexto a la IA; el archivo docs/ROADMAP.md es el canónico para seguimiento y PRs.

---

## Planes y monetización

- Plan gratuito:
   - Escaneo local (addon), análisis básico con histórico limitado, IA local.
   - Límite diario de consultas al histórico remoto.
- Plan Premium (mensual/trimestral):
   - Histórico 12 meses, comparativas multi-servidor/facción, IA en la nube con contexto ampliado.
   - Alertas en tiempo real y reportes automáticos.
   - Acceso controlado por API Key y endpoint `/premium-check`.

Detalles en `docs/monetization.md`.

---

Este README proporciona una visión completa del proyecto, tanto para usuarios como para desarrolladores. Si necesitas más detalles, consulta la documentación en la carpeta `docs/`. ¡Disfruta explorando el mercado con Kezan Protocol! 🚀

---

## Documentación y build de docs

- Documentación de API (pdoc) ya generada en `docs/` (HTML estático).
- Regenerar documentación de módulos:
   ```powershell
   python -m pip install pdoc
   pdoc -o docs kezan
   ```
- Exportar a Word/PDF (a partir de HTML):
   ```powershell
   python .\docs\generate_documents.py
   ```

En `docs/index.html` hay enlaces rápidos a la guía maestra y requisitos de IA.

---

## Documentación de trabajo (docs/temp_flow)
Para notas y borradores en curso utiliza:
- docs/temp_flow/

Importante: docs/temp_flow no es fuente de verdad. Cuando un contenido madure, muévelo a:
- Documentación oficial: docs/*.md
- Roadmap canónico: docs/ROADMAP.md

---

## Política de versiones y changelog

- Versionado semántico: MAJOR.MINOR.PATCH.
- Todo cambio visible (feat/fix/perf/docs/tests/chore) debe añadirse a `CHANGELOG.md` con fecha y breve descripción.
- Nuevas features o cambios de uso deben actualizar README y `docs/`.
- Los PRs deben marcar las casillas de actualización de changelog y docs (ver plantilla de PR).

Skips intencionales en pruebas:
- `tests/test_market_optimizer_chunks_context.py`: deshabilitado por redundancia con otras pruebas de `market_optimizer`.
- `tests/test_coverage_uplift.py`: salta si `numpy` no está instalado (evita dependencia dura en entornos mínimos; `market_optimizer` realiza import perezoso de NumPy en runtime).
