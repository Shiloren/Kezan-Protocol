# 🧠 Kezan Protocol

Kezan Protocol es un asistente local que analiza la casa de subastas de World of Warcraft y genera recomendaciones de compra y venta usando modelos de lenguaje ejecutados en tu propio equipo.

## Índice
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración inicial](#configuración-inicial)
- [Ejecución](#ejecución)
  - [API HTTP](#api-http)
  - [Interfaz de escritorio](#interfaz-de-escritorio)
- [Flujo de datos paso a paso](#flujo-de-datos-paso-a-paso)
- [Módulos principales](#módulos-principales)
- [Generar documentación](#generar-documentación)
- [Pruebas](#pruebas)
- [Errores comunes](#errores-comunes)

## Arquitectura

1. **Extracción de datos** – `blizzard_api` obtiene un token OAuth y descarga las subastas del reino configurado.
2. **Análisis de mercado** – `analyzer` filtra los lotes más rentables y los formatea con `formatter`.
3. **Análisis de crafteo** – `crafting_analyzer` evalúa recetas usando precios de mercado.
4. **IA local** – `llm_interface` envía los datos a un modelo local (Ollama, LM Studio, etc.) para producir recomendaciones en español.
5. **API y UI** – `api` expone endpoints REST, `main` monta la app de FastAPI y la interfaz en `frontend/` (Tauri + React) consulta dichos endpoints ofreciendo una experiencia de escritorio.
6. **Persistencia y utilidades** – `cache` almacena tokens y resultados, `context_memory` guarda históricos, `export` permite volcar datos a CSV/JSON y `logger` mantiene registros rotativos.

## Requisitos

- Python 3.8–3.12
- Dependencias listadas en `requirements.txt`
- Credenciales de la API de Blizzard y un LLM local accesible por HTTP

## Instalación

```bash
git clone https://github.com/.../Kezan-Protocol.git
cd Kezan-Protocol
pip install -r requirements.txt
```

## Configuración inicial

1. Copia `example.env` a `.env` y completa tus datos.
2. Ejecuta el inicializador para validar las credenciales:

```bash
python -m kezan.initializer
```

Este script comprueba las claves con Blizzard y almacena los valores en `.env`.

## Ejecución

### API HTTP

Inicia el servicio FastAPI:

```bash
uvicorn main:app --reload
```

Endpoints disponibles:

- `GET /api/gangas` – lotes de subasta con mejor margen.
- `GET /api/consejo` – recomendaciones de compra/venta usando la IA.
- `GET /api/crafteables` – recetas rentables para una profesión.

### Interfaz de escritorio

La interfaz moderna se construye con **Tauri + React** y consume las rutas API:

```bash
cd frontend
npm install
npm run dev    # durante el desarrollo
npm run build  # generar ejecutable
```

## Flujo de datos paso a paso

1. **Token OAuth** – `get_access_token` solicita y cachea un token válido.
2. **Descarga de subastas** – `fetch_auction_data` usa dicho token y almacena la respuesta cinco minutos.
3. **Análisis** – `get_top_items` calcula margen estimado y devuelve los mejores lotes.
4. **Formateo** – `format_for_ai` añade nombres legibles de los ítems y porcentajes.
5. **Consulta IA** – `analyze_items_with_llm` envía la lista al modelo local y devuelve recomendaciones.
6. **Respuesta API/GUI** – la ruta `/api/consejo` combina todo y la interfaz gráfica muestra el análisis.

## Módulos principales

| Módulo | Descripción |
|--------|-------------|
| `blizzard_api` | OAuth2 y descarga de datos de subasta. |
| `analyzer` | Filtra lotes con mayor margen. |
| `crafting_analyzer` | Calcula costos y beneficio de recetas de profesiones. |
| `llm_interface` | Comunicación con modelos de lenguaje locales. |
| `formatter` | Normaliza datos para la IA y resuelve nombres de ítems. |
| `cache` | Cache simple persistente con TTL. |
| `context_memory` | Historial de análisis con políticas de limpieza. |
| `export` | Exportación a JSON/CSV. |
| `logger` | Configuración común de logging. |

## Generar documentación

La carpeta `docs/` contiene la documentación HTML. Para crear versiones en Word y PDF:

```bash
python docs/generate_documents.py
```

Los archivos se guardarán en `docs/documentacion_completa.docx` y `docs/documentacion_interna.pdf`.

## Pruebas

Ejecuta la suite de tests automatizados:

```bash
pytest
```

## Errores comunes

- **"Las claves de la API de Blizzard no están configuradas."** – asegúrate de que `.env` contiene `BLIZZ_CLIENT_ID` y `BLIZZ_CLIENT_SECRET`.
- **"El modelo de IA local no está activo o no responde."** – confirma que el servicio en `LLM_API_URL` está en funcionamiento.
