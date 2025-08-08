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
