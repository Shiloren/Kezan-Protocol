import json
import os
import time
from typing import List, Dict, Optional

import requests
import logging

# Configuration for the local LLM endpoint
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))


def analyze_items_with_llm(data: List[Dict]) -> str:
    """Send auction item data to a local LLM for analysis.

    Parameters
    ----------
    data: List[Dict]
        List of auction items already formatted for AI consumption.

    Returns
    -------
    str
        Textual recommendation produced by the local LLM.

    Raises
    ------
    RuntimeError
        If the local model is not reachable or returns an invalid response.
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
        response = requests.post(LLM_API_URL, json=payload, timeout=30)
        elapsed = time.perf_counter() - start
        response.raise_for_status()
        content = response.json().get("response", "").strip()
        if not content:
            raise RuntimeError("Respuesta vacía del modelo de IA.")
        logging.getLogger(__name__).info("LLM analysis took %.2fs", elapsed)
        return content
    except requests.RequestException as exc:
        raise RuntimeError(
            "El modelo de IA local no está activo o no responde."
        ) from exc


def analyze_recipes_with_llm(data: List[Dict], inventory: Optional[List[int]] = None) -> str:
    """Evaluate crafting recipes using the local LLM.

    Parameters
    ----------
    data: List[Dict]
        List of recipe analysis dictionaries. Each entry should include
        at minimum ``recipe_id`` and ``profit`` fields.
    inventory: Optional[List[int]]
        Optional list of item IDs that the user already possesses.  This
        allows the model to reason about which crafts are more convenient
        given existing materials.

    Returns
    -------
    str
        Recommendation text produced by the LLM.
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
        response = requests.post(LLM_API_URL, json=payload, timeout=30)
        elapsed = time.perf_counter() - start
        response.raise_for_status()
        content = response.json().get("response", "").strip()
        if not content:
            raise RuntimeError("Respuesta vacía del modelo de IA.")
        logging.getLogger(__name__).info("LLM recipe analysis took %.2fs", elapsed)
        return content
    except requests.RequestException as exc:  # pragma: no cover - network errors
        raise RuntimeError(
            "El modelo de IA local no está activo o no responde."
        ) from exc

