"""Interface para analizar datos mediante un LLM local."""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from kezan.config import LOCAL_MODELS_PATH, validate_local_model_path

# Configuración para el endpoint local del LLM
LLM_API_URL = os.getenv(
    "LLM_API_URL", "http://localhost:11434/api/generate"
)
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))

logger = logging.getLogger(__name__)


def load_model_template(name: str) -> None:
    """Load a local IA template and update runtime configuration."""
    if not validate_local_model_path():
        raise FileNotFoundError(
            f"Directorio de modelos no encontrado: {LOCAL_MODELS_PATH}"
        )

    template_path = Path(LOCAL_MODELS_PATH) / f"{name}.json"
    if not template_path.is_file():
        raise FileNotFoundError(
            f"No se encontró la plantilla de IA: {template_path}"
        )

    try:
        data = json.loads(template_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - invalid template
        raise ValueError("Plantilla de IA inválida") from exc

    if "model" not in data:
        raise ValueError("La plantilla debe contener la clave 'model'")

    global LLM_MODEL, LLM_API_URL, LLM_TEMPERATURE, LLM_TOP_P
    LLM_MODEL = data.get("model", LLM_MODEL)
    LLM_API_URL = data.get("api_url", LLM_API_URL)
    LLM_TEMPERATURE = float(data.get("temperature", LLM_TEMPERATURE))
    LLM_TOP_P = float(data.get("top_p", LLM_TOP_P))


def analyze_items_with_llm(data: List[Dict]) -> str:
    """Envía datos de subasta a un LLM local para su análisis.

    Parámetros:
    - data (List[Dict]): lista de items formateados para la IA.

    Retorna:
    - str: recomendación generada por el modelo.

    Lanza:
    - RuntimeError: si el modelo no responde o la respuesta es inválida.
    """
    prompt = (
        "Eres un asistente experto en el mercado de World of Warcraft. "
        "Analiza los siguientes items y recomienda las mejores compras "
        "en Español:\n"
        f"{json.dumps(data, ensure_ascii=False)}"
    )

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": LLM_TEMPERATURE,
        "top_p": LLM_TOP_P,
    }

    try:
        start = time.perf_counter()
        response = httpx.post(LLM_API_URL, json=payload, timeout=30)
        elapsed = time.perf_counter() - start
        response.raise_for_status()
        try:
            content = response.json().get("response", "").strip()
        except (ValueError, KeyError) as exc:
            raise RuntimeError("Respuesta inválida del modelo de IA") from exc
        if not content:
            raise RuntimeError("Respuesta vacía del modelo de IA.")
        logger.info("LLM analysis took %.2fs", elapsed)
        return content
    except httpx.HTTPError as exc:
        raise RuntimeError(
            "El modelo de IA local no está activo o no responde."
        ) from exc


def analyze_recipes_with_llm(
    data: List[Dict], inventory: Optional[List[int]] = None
) -> str:
    """Evalúa recetas de crafteo usando el LLM local.

    Parámetros:
    - data (List[Dict]): resultados de análisis de recetas.
    - inventory (Optional[List[int]]): IDs de items ya disponibles.

    Retorna:
    - str: texto de recomendación generado por el modelo.
    """
    prompt = (
        "Eres un maestro artesano de World of Warcraft. Analiza las "
        "siguientes recetas y recomienda los crafteos más rentables en "
        "Español:\n"
        f"{json.dumps(data, ensure_ascii=False)}"
    )
    if inventory:
        prompt += (
            "\nTen en cuenta que ya poseo en mi inventario: "
            f"{inventory}."
        )

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": LLM_TEMPERATURE,
        "top_p": LLM_TOP_P,
    }

    try:
        start = time.perf_counter()
        response = httpx.post(LLM_API_URL, json=payload, timeout=30)
        elapsed = time.perf_counter() - start
        response.raise_for_status()
        try:
            content = response.json().get("response", "").strip()
        except (ValueError, KeyError) as exc:
            raise RuntimeError("Respuesta inválida del modelo de IA") from exc
        if not content:
            raise RuntimeError("Respuesta vacía del modelo de IA.")
        logger.info("LLM recipe analysis took %.2fs", elapsed)
        return content
    except httpx.HTTPError as exc:  # pragma: no cover - network errors
        raise RuntimeError(
            "El modelo de IA local no está activo o no responde."
        ) from exc
