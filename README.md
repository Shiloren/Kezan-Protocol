# 🧠 Kezan Protocol

**Kezan Protocol** es un asistente inteligente de análisis de mercado para World of Warcraft, diseñado para ayudarte a identificar oportunidades de reventa, crafting rentable y gangas en tiempo real dentro de la casa de subastas.

Inspirado en la astucia de los goblins y potenciado por modelos de IA locales, este sistema convierte datos crudos del mercado en estrategias de oro optimizadas para tu perfil de jugador.

---

## 📌 Objetivo

Crear un sistema local capaz de:

- Analizar el mercado de subastas de WoW en tiempo real.
- Detectar ítems con alto margen de beneficio.
- Recomendar oportunidades de flipping o transformación con profesiones.
- Interactuar mediante comandos simples en consola, chat o web ligera.
- Conectarse a una IA local para ofrecer estrategias personalizadas.

---

## 🏗️ Arquitectura del sistema

### 1. Motor de IA local

- **Modelo**: GPT-OSS-20B (OpenAI, open-weight)
- **Entorno**: PC local con GPU (RTX 3060 8GB)
- **Framework**: Ollama / llama.cpp / LM Studio (según preferencia)

---

### 2. Fuente de datos

- **Primario**: API oficial de Blizzard
  `https://{region}.api.blizzard.com/data/wow/connected-realm/{realmId}/auctions`
  Requiere OAuth2 + `namespace=dynamic-{region}`

- **Alternativas**:
  - Exportaciones JSON desde el addon TradeSkillMaster.
  - Scraping de webs públicas (limitado).

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

---
