"""Interface para analizar datos mediante un LLM local."""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from kezan.config import LOCAL_MODELS_PATH, validate_local_model_path
from kezan.compliance import advisory_preamble, sanitize_dsl_text

# Configuración para el endpoint local del LLM
LLM_API_URL = os.getenv(
    "LLM_API_URL", "http://localhost:11434/api/generate"
)
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
# Opcional para LM Studio / servidores OpenAI-compatibles
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

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
        advisory_preamble() + "\n" +
        "Eres un asistente experto en el mercado de World of Warcraft. "
        "Analiza los siguientes items y recomienda las mejores compras "
        "en Español (modo asesor). Devuelve recomendaciones en DSL permitido y breve explicación.\n"
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
        return sanitize_dsl_text(content)
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
        advisory_preamble() + "\n" +
        "Eres un maestro artesano de World of Warcraft. Analiza las "
        "siguientes recetas y recomienda los crafteos más rentables en "
        "Español (modo asesor). Devuelve DSL permitido y breve explicación.\n"
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
        return sanitize_dsl_text(content)
    except httpx.HTTPError as exc:  # pragma: no cover - network errors
        raise RuntimeError(
            "El modelo de IA local no está activo o no responde."
        ) from exc


class LLMInterface:
    def __init__(self):
        self.model = LLM_MODEL
        self.api_url = LLM_API_URL
        self.temperature = LLM_TEMPERATURE
        self.top_p = LLM_TOP_P

    def analyze_items(self, data: List[Dict]) -> str:
        return analyze_items_with_llm(data)

    def analyze_recipes(self, data: List[Dict], inventory: Optional[List[int]] = None) -> str:
        return analyze_recipes_with_llm(data, inventory)

    async def analyze_intent(self, query: str) -> dict:
        """Analiza la intención del usuario y retorna un dict seguro.

        Intenta obtener JSON desde el LLM; si no es válido, retorna una estructura por defecto.
        """
        prompt = (
            advisory_preamble() + "\n" +
            "Analiza la siguiente consulta y determina la intención del usuario y las acciones necesarias.\n"
            "Responde SOLO en JSON con las claves: type, operation, requires_api_call (bool), requires_file_access (bool), endpoint (opcional), params (obj opcional), file_path (opcional).\n\n"
            f"Consulta: {query}"
        )
        try:
            content = await self._post_async(prompt)
            intent = json.loads(content)
            if not isinstance(intent, dict):
                raise ValueError("Intent no es dict")
            intent.setdefault("type", "unknown")
            intent.setdefault("operation", None)
            intent.setdefault("requires_api_call", False)
            intent.setdefault("requires_file_access", False)
            return intent
        except Exception as exc:
            logger.warning("Intent no parseable: %s", exc)
            return {
                "type": "unknown",
                "operation": None,
                "requires_api_call": False,
                "requires_file_access": False,
            }

    async def scan_auction_house(self, current_data: List[Dict], profile_preferences: Dict, game_version: str) -> List[Dict]:
        """Escaneo de subastas: devuelve lista de oportunidades estructuradas.

        Salida esperada: lista de objetos { item_id: int, price: int, quantity: int }
        """
        prompt = (
            advisory_preamble() + "\n" +
            "Analiza el mercado y devuelve oportunidades como una lista JSON.\n"
            "Cada elemento debe tener: item_id (int), price (int), quantity (int).\n"
            f"Version: {game_version}\n"
            f"Preferencias: {json.dumps(profile_preferences, ensure_ascii=False)}\n"
            f"Datos: {json.dumps(current_data[:200], ensure_ascii=False)}\n"  # limitar tamaño
        )
        try:
            content = await self._post_async(prompt, timeout=45)
            data = json.loads(content)
            if isinstance(data, list):
                cleaned = []
                for it in data:
                    if not isinstance(it, dict):
                        continue
                    if {"item_id", "price", "quantity"}.issubset(it.keys()):
                        cleaned.append({
                            "item_id": int(it["item_id"]),
                            "price": int(it["price"]),
                            "quantity": int(it["quantity"]),
                        })
                return cleaned
            return []
        except Exception as exc:
            logger.error("Error en scan_auction_house: %s", exc)
            return []

    def suggest_search_strategy(self, item_history: List[Dict], market_trends: List[Dict], game_version: str) -> str:
        """Sugerir estrategia (método síncrono para compatibilidad actual)."""
        prompt = (
            advisory_preamble() + "\n" +
            "Propón una estrategia breve de búsqueda basada en histórico y tendencias (modo asesor).\n"
            f"Version: {game_version}\n"
            f"Histórico: {json.dumps(item_history[-10:], ensure_ascii=False)}\n"
            f"Tendencias: {json.dumps(market_trends[-10:], ensure_ascii=False)}\n"
            "Responde en 2-3 frases concisas."
        )
        try:
            return self._post_sync(prompt)
        except Exception as exc:
            logger.warning("Fallback suggest_search_strategy por error: %s", exc)
            return "Prioriza items con caídas recientes vs media y volumen alto; ajusta umbrales por volatilidad."

    async def analyze_market_opportunity(self, item_data: Dict, historical_prices: List[Dict]) -> Dict:
        """Analiza oportunidad de mercado y devuelve dict estructurado o fallback."""
        prompt = (
            advisory_preamble() + "\n" +
            "Eres un analista de subastas. Analiza la siguiente oportunidad de mercado con foco práctico.\n"
            "Devuelve SOLO JSON con las claves: analysis (string), opportunity (bool), reason (string).\n\n"
            f"Datos actuales: {json.dumps(item_data, ensure_ascii=False)}\n"
            f"Historial: {json.dumps(historical_prices[-10:], ensure_ascii=False)}"
        )
        try:
            content = await self._post_async(prompt)
            data = json.loads(content)
            if isinstance(data, dict):
                return data
            return {"analysis": content or "", "opportunity": False, "reason": "unparsed"}
        except Exception as exc:
            logger.error("Error en analyze_market_opportunity: %s", exc)
            return {"analysis": "", "opportunity": False, "reason": str(exc)}

    def _is_openai_style(self) -> bool:
        """Heurística simple: si la URL contiene /v1/ asumimos OpenAI-compatible (LM Studio)."""
        return "/v1/" in (self.api_url or "")

    def _build_payload_headers(self, prompt: str) -> Dict:
        """Construye payload y headers según tipo de servidor (Ollama vs OpenAI)."""
        headers = {}
        if self._is_openai_style():
            if LLM_API_KEY:
                headers["Authorization"] = f"Bearer {LLM_API_KEY}"
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": False,
            }
        else:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
        return {"payload": payload, "headers": headers}

    def _extract_text(self, resp_json: Dict) -> str:
        """Extrae texto del JSON tanto para Ollama (/api/generate) como OpenAI (/v1/*)."""
        if isinstance(resp_json, dict) and "response" in resp_json:
            return (resp_json.get("response") or "").strip()
        try:
            choices = resp_json.get("choices") or []
            if not choices:
                return ""
            first = choices[0]
            if isinstance(first, dict):
                if "message" in first and first["message"]:
                    return (first["message"].get("content") or "").strip()
                if "text" in first:
                    return (first.get("text") or "").strip()
        except Exception:
            return ""
        return ""

    async def _post_async(self, prompt: str, timeout: int = 30) -> str:
        cfg = self._build_payload_headers(prompt)
        start = time.perf_counter()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.api_url,
                json=cfg["payload"],
                headers=cfg["headers"],
                timeout=timeout,
            )
        elapsed = time.perf_counter() - start
        resp.raise_for_status()
        content = self._extract_text(resp.json())
        logger.info("LLM request took %.2fs", elapsed)
        return content

    def _post_sync(self, prompt: str, timeout: int = 20) -> str:
        cfg = self._build_payload_headers(prompt)
        resp = httpx.post(
            self.api_url,
            json=cfg["payload"],
            headers=cfg["headers"],
            timeout=timeout,
        )
        resp.raise_for_status()
        return self._extract_text(resp.json())
