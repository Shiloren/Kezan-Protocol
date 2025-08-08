"""Interface para analizar datos mediante un LLM local."""

import json
import os
import time
from typing import List, Dict, Optional

import httpx
import logging

# Configuración para el endpoint local del LLM
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))


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
        "Analiza los siguientes items y recomienda las mejores compras en Español:\n"
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
        content = response.json().get("response", "").strip()
        if not content:
            raise RuntimeError("Respuesta vacía del modelo de IA.")
        logging.getLogger(__name__).info("LLM analysis took %.2fs", elapsed)
        return content
    except httpx.HTTPError as exc:
        raise RuntimeError(
            "El modelo de IA local no está activo o no responde."
        ) from exc


def analyze_recipes_with_llm(data: List[Dict], inventory: Optional[List[int]] = None) -> str:
    """Evalúa recetas de crafteo usando el LLM local.

    Parámetros:
    - data (List[Dict]): resultados de análisis de recetas.
    - inventory (Optional[List[int]]): IDs de items ya disponibles.

    Retorna:
    - str: texto de recomendación generado por el modelo.
    """
    prompt = (
        "Eres un maestro artesano de World of Warcraft. Analiza las "
        "siguientes recetas y recomienda los crafteos más rentables en Español:\n"
        f"{json.dumps(data, ensure_ascii=False)}"
    )
    if inventory:
        prompt += f"\nTen en cuenta que ya poseo en mi inventario: {inventory}."

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
        content = response.json().get("response", "").strip()
        if not content:
            raise RuntimeError("Respuesta vacía del modelo de IA.")
        logging.getLogger(__name__).info("LLM recipe analysis took %.2fs", elapsed)
        return content
    except httpx.HTTPError as exc:  # pragma: no cover - network errors
        raise RuntimeError(
            "El modelo de IA local no está activo o no responde."
        ) from exc

