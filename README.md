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

1. **Extracción de datos**
   - `blizzard_api`: Obtiene un token OAuth y descarga las subastas del reino configurado.

2. **Análisis de mercado**
   - `analyzer`: Filtra los lotes más rentables y los formatea con `formatter`.

3. **Análisis de crafteo**
   - `crafting_analyzer`: Evalúa recetas usando precios de mercado.

4. **IA local (asesoría-only, Blizzard-safe)**
   - `llm_interface`: Envía los datos a un modelo local (Ollama o servidores OpenAI-compatibles como LM Studio) y aplica guardarraíles de cumplimiento (`compliance`) para generar recomendaciones en español usando una DSL de solo asesoría.

5. **API y UI**
   - `api`: Expone endpoints REST.
   - `frontend/`: Interfaz de usuario basada en Tauri + React.

6. **Persistencia y utilidades**
   - `cache`: Almacena tokens y resultados.
   - `context_memory`: Guarda históricos.
   - `export`: Permite volcar datos a CSV/JSON.
   - `logger`: Mantiene registros rotativos.

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
2. Configura las credenciales de la API de Blizzard (`BLIZZ_CLIENT_ID`, `BLIZZ_CLIENT_SECRET`).
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

Este README proporciona una visión completa del proyecto, tanto para usuarios como para desarrolladores. Si necesitas más detalles, consulta la documentación en la carpeta `docs/`. ¡Disfruta explorando el mercado con Kezan Protocol! 🚀
