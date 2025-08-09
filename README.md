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

4. **IA local**
   - `llm_interface`: Envía los datos a un modelo local (Ollama, LM Studio, etc.) para producir recomendaciones en español.

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
- **Backend**: Python 3.10+
- **Frontend**: Node.js 16+, npm 8+
- **Dependencias**: Ver `requirements.txt` y `package.json`.

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
4. `llm_interface` genera recomendaciones.
5. Los resultados se muestran en la interfaz o se exponen vía API.

---

## Módulos principales
- **`blizzard_api`**: Gestión de autenticación y descarga de datos.
- **`analyzer`**: Análisis de subastas.
- **`crafting_analyzer`**: Evaluación de recetas.
- **`llm_interface`**: Integración con modelos de lenguaje.
- **`frontend/`**: Interfaz de usuario.

---

## Pruebas
Ejecuta las pruebas unitarias:
```bash
pytest tests/
```

---

## Errores comunes
1. **Error de credenciales**:
   - Asegúrate de configurar correctamente el archivo `.env`.

2. **Problemas con dependencias**:
   - Verifica que las versiones de Python y Node.js sean compatibles.

---

Este README proporciona una visión completa del proyecto, tanto para usuarios como para desarrolladores. Si necesitas más detalles, consulta la documentación en la carpeta `docs/`. ¡Disfruta explorando el mercado con Kezan Protocol! 🚀
