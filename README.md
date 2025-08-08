# 🧠 Kezan Protocol

**Kezan Protocol** es un asistente inteligente de análisis de mercado para World of Warcraft, diseñado para ayudarte a identificar oportunidades de reventa, crafting rentable y gangas en tiempo real dentro de la casa de subastas.

Inspirado en la astucia de los goblins y potenciado por modelos de IA locales, este sistema convierte datos crudos del mercado en estrategias de oro optimizadas para tu perfil de jugador.

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

## 📌 Objetivo

Crear un sistema local capaz de:

- Analizar el mercado de subastas de WoW en tiempo real.
- Detectar ítems con alto margen de beneficio.
- Recomendar oportunidades de flipping o transformación con profesiones.
- Interactuar mediante comandos simples en consola, chat o web ligera.
- Conectarse a una IA local para ofrecer estrategias personalizadas.

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

## 🏗️ Arquitectura del sistema

### 1. Motor de IA local

- **Modelo**: GPT-OSS-20B (OpenAI, open-weight)
- **Entorno**: PC local con GPU (RTX 3060 8GB)
- **Framework**: Ollama / llama.cpp / LM Studio (según preferencia)

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

### 2. Fuente de datos

- **Primario**: API oficial de Blizzard
  `https://{region}.api.blizzard.com/data/wow/connected-realm/{realmId}/auctions`
  Requiere OAuth2 + `namespace=dynamic-{region}`

- **Alternativas**:
  - Exportaciones JSON desde el addon TradeSkillMaster.
  - Scraping de webs públicas (limitado).

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

### 3. Backend

- **Lenguaje**: Python
- **Framework**: FastAPI
- **Base de datos**: SQLite o PostgreSQL
- **Lógica**:
  - Conexión a la API
  - Análisis de márgenes de beneficio
  - Filtrado por categorías y beneficios
  - Generación de resúmenes para IA

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

### 4. Interfaz

**Modos posibles**:

- Terminal interactivo (CLI)
- Web ligera (FastAPI + frontend opcional)
- Chat local con IA

**Comandos esperados**:

- `Muéstrame las 5 gangas del día`
- `Filtra solo consumibles con margen > 30%`
- `¿Qué objetos puedo revender ahora con al menos 10g de beneficio?`

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

## 🧠 Conexión con IA

El backend estructura los datos en formato entendible para la IA:

```json
{
  "items": [
    {
      "name": "Black Lotus",
      "ah_price": 92,
      "avg_sell_price": 145,
      "stack_size": 1,
      "estimated_margin": "57%"
    }
  ]
}
```

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

## 📦 Requisitos del sistema

- CPU moderna con al menos 4 núcleos.
- 8 GB de RAM (16 GB recomendados si ejecutas WoW y la IA al mismo tiempo).
- Python 3.8–3.12 instalado (no se recomiendan versiones 3.13+).
- Un modelo de lenguaje local (por ejemplo, `llama3`) servido desde Ollama o LM Studio.

## 🚀 Instalación rápida (ejecutable)

1. Descarga el ejecutable desde la sección de lanzamientos.
2. Copia tu archivo `.env` en la misma carpeta que el ejecutable.
3. Ejecuta `KezanAI` con doble clic o desde la terminal.

> ℹ️ El archivo `.env` **no** se incrusta en el binario; debe estar siempre junto al ejecutable.

### Compilación manual desde el código fuente

Si necesitas generar el ejecutable tú mismo y evitar errores como `ModuleNotFoundError: No module named 'httpx'`, instala PyInstaller e incluye la dependencia explícitamente:

```bash
pip install -r requirements.txt
pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "KezanProtocol" --hidden-import=httpx desktop_app.py
# o usando el archivo .spec incluido
python -m PyInstaller KezanProtocol.spec
```

## 💻 Uso

1. Abre World of Warcraft.
2. Inicia **KezanAI**.
3. Pulsa **"Actualizar Datos"** para consultar la casa de subastas.
4. Observa el análisis de la IA y las recomendaciones de compra o venta.

## 🔧 Variables de entorno `.env`

```ini
BLIZZ_CLIENT_ID=
BLIZZ_CLIENT_SECRET=
REGION=eu
REALM_ID=1080
LM_ENDPOINT=http://localhost:11434
LM_MODEL=llama3
```

## 🛠️ Solución de errores comunes

- **"No se puede conectar al modelo IA"**: verifica que Ollama o LM Studio esté abierto y accesible en `LM_ENDPOINT`.
- **"API keys no configuradas"**: asegúrate de definir `BLIZZ_CLIENT_ID` y `BLIZZ_CLIENT_SECRET` en tu archivo `.env`.
- **El ejecutable se cierra al abrirse**: confirma que el archivo `.env` se encuentre junto al ejecutable y que ningún antivirus lo esté bloqueando.

## 📄 Generar documentación en Word/PDF

La documentación en formatos `.docx` y `.pdf` puede generarse localmente a partir de los archivos HTML en `docs/`.

```bash
pip install -r requirements.txt
python docs/generate_documents.py
```

Los archivos resultantes se guardarán en el mismo directorio `docs/`.

---

