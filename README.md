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
Ejecuta el backend con FastAPI:
```bash
python main.py
```

### Interfaz de escritorio
Ejecuta la aplicación Tauri:
```bash
cd frontend
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
- **`blizzard_api`**: Gestión de autenticación y descarga de datos.
- **`analyzer`**: Análisis de subastas.
- **`crafting_analyzer`**: Evaluación de recetas.
- **`llm_interface`**: Integración con modelos de lenguaje.
- **`frontend/`**: Interfaz de usuario.

---

## Pruebas y cobertura
Ejecuta las pruebas unitarias y genera cobertura en terminal:
```bash
pytest -q --disable-warnings --cov=kezan --cov-report=term-missing
```

Para reporte HTML limpio:
```bash
rd /s /q htmlcov  # Windows
pytest -q --disable-warnings --cov=kezan --cov-report=html
```

Áreas nuevas cubiertas por tests:
- `llm_interface`: rutas síncronas/asíncronas, Ollama vs OpenAI-style, fallbacks seguros.
- `ai_controller`: límites de tasa, validaciones de operación/archivos, persistencia de memoria.

### Análisis estático
```bash
ruff check .
black --check .
```

### Dependencias
- Python:
  ```bash
  pip list --outdated
  pip-audit -r requirements.txt
  ```
- Frontend:
  ```bash
  npm outdated
  npm audit
  ```

---

## Errores comunes
1. **Error de credenciales**:
   - Asegúrate de configurar correctamente el archivo `.env`.

2. **Problemas con dependencias**:
   - Verifica que las versiones de Python y Node.js sean compatibles.

---

## Guía maestra del proyecto
Para la visión, arquitectura, DSL de asesoría y guardarraíles Blizzard-safe, consulta:

- docs/kezan_protocol_master_prompt.md

Toda nueva funcionalidad debe alinearse con esta guía. Si surgen decisiones de arquitectura o criterios adicionales, añade esa información al documento y versiona el cambio.

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
