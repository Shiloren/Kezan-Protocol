# Guía de Contribución

¡Gracias por tu interés en contribuir al Kezan Protocol! Esta guía te ayuda a configurar tu entorno y alinea el proceso de PRs con la visión del proyecto.

Antes de empezar, revisa y respeta el documento maestro:
- `docs/kezan_protocol_master_prompt.md`

## Configuración del entorno (Windows PowerShell)

### Requisitos previos
- Python 3.12+
- Node.js 18+
- Rust (para Tauri UI)

### Pasos
```powershell
# Clonar y preparar entorno
git clone https://github.com/Shiloren/Kezan-Protocol.git
cd Kezan-Protocol
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Variables de entorno
Copy-Item example.env .env
# Edita .env con BLIZZ_* / BLIZZARD_* / REGION / REALM_ID

# API local (ASGI)
python -m pip install uvicorn
uvicorn main:app --reload

# UI (opcional)
cd frontend
npm install
npm run dev:tauri
```

## Estructura del proyecto
- `kezan/` código Python (API, análisis, LLM, etc.)
- `frontend/` Tauri/React
- `tests/` pruebas unitarias
- `docs/` documentación generada y guías

## Estilo y calidad
- Python: `black --check .`, `ruff check .`, type hints, docstrings.
- JS/React: ESLint/Prettier (si aplica en el futuro), componentes funcionales.

## Tests y cobertura
```powershell
pytest -q --disable-warnings --cov=kezan --cov-report=term-missing
# Reporte HTML
if (Test-Path htmlcov) { Remove-Item htmlcov -Recurse -Force }
pytest -q --disable-warnings --cov=kezan --cov-report=html
```
Objetivo de cobertura: ≥95%.

Notas:
- `market_optimizer` usa NumPy en runtime; instala `numpy` si lo necesitas. Las pruebas usan un shim cuando no está presente.
- Para LLM local, usa `LLM_API_URL`, `LLM_MODEL` y (OpenAI-style) `LLM_API_KEY`.

## Documentación
Generar docs de módulos (pdoc) hacia `docs/` y exportar a Word/PDF:
```powershell
python -m pip install pdoc
pdoc -o docs kezan
python .\docs\generate_documents.py
```

## Proceso de PR
1. Crea rama: `git checkout -b feat/nombre-breve`.
2. Implementa con tests y docstrings.
3. Ejecuta linters y tests con cobertura.
4. Actualiza README/Docs si cambia el uso o configuración.
5. Abre PR con resumen, impacto, y resultados de tests/cobertura.

Checklist de PRs:
- [ ] Alineado con `docs/kezan_protocol_master_prompt.md` (visión/arquitectura/DSL)
- [ ] Tests añadidos/actualizados y cobertura ≥95% si aplica
- [ ] Sin romper API pública; anota breaking changes si existen
- [ ] README/Docs actualizados

## Reporte de bugs
- Abre un issue con: descripción, pasos, esperado vs actual, logs y entorno.

¡Gracias por contribuir! 🧠💼
