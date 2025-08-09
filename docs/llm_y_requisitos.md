# IA local y requisitos del sistema

## Soporte de backends LLM
- Ollama (`/api/generate`): usa `model`, `prompt`, `temperature`, `top_p`.
- OpenAI-style (LM Studio, otros) (`/v1/chat/completions`): usa `messages`, `model`, headers `Authorization` si aplica.

Configura via variables de entorno:
- `LLM_API_URL` (por defecto `http://localhost:11434/api/generate`)
- `LLM_MODEL` (por defecto `mistral`)
- `LLM_API_KEY` (opcional para OpenAI-style)
- `LLM_TEMPERATURE`, `LLM_TOP_P`

Plantillas: `templates/*.json` y función `load_model_template(nombre)`.

## DSL asesoría (Blizzard-safe)
Acciones permitidas:
- `RECOMMEND_BUY(qty,target,eta_h)`
- `RECOMMEND_CRAFT(qty,target,eta_h)`
- `SET(key,value)`, `ALERT(type,msg)`, `WATCHLIST(tag)`
- `SIMULATE(days,strategy)`, `SKIP(reason)`, `NOTIFY(channel)`
- `OPEN_AH_SEARCH(query)`, `COPY_POST_STRING(text)`

Acciones prohibidas (se sanea automáticamente): `BUY`, `CRAFT`, `POST`, `UNDERCUT`, etc.

## Requisitos del sistema
- CPU: 4c mínimo; 8c+ recomendado con IA.
- RAM: 8 GB mínimo; 16 GB recomendado; 24-32 GB para modelos >8B.
- Disco: 2 GB app/logs; 10-30 GB si instalas múltiples modelos.
- GPU (opcional): 6 GB VRAM mínimo práctico para 7B cuantizado; 12+ GB recomendado.
- SO: Windows 10/11, macOS 13+, Linux x86_64.

## Consejos de rendimiento
- Para CPU: usar modelos cuantizados (q4_0/q5_0) y bajar `temperature`.
- Para GPU: habilitar soporte CUDA/Metal según backend.
- Limitar tamaño de prompts (en `llm_interface` ya se recorta entrada en algunas rutas).

## Pruebas
- Cobertura objetivo: 80%+. Ejecuta:
```
pytest -q --disable-warnings --cov=kezan --cov-report=html
```
