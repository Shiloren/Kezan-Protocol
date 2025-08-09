"""Controlador de IA para gestionar operaciones autónomas y aprendizaje."""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
import os

from .blizzard_api import BlizzardAPI
from .profile_manager import ProfileManager, GameVersion
from .llm_interface import LLMInterface
from .logger import get_logger

@dataclass
class AIControllerConfig:
    """Configuración para el controlador de IA."""
    max_requests_per_minute: int = 100
    cache_duration: int = 3600  # 1 hora
    auto_learn: bool = True
    memory_file: str = "ai_memory.json"
    allowed_operations: List[str] = None  # None = todas las operaciones permitidas

class AIController:
    def __init__(self, config: Optional[AIControllerConfig] = None):
        """
        Inicializa el controlador de IA.
        
        Args:
            config: Configuración personalizada. Si no se proporciona, se usa la configuración por defecto.
        """
        self.config = config or AIControllerConfig()
        self.blizzard_api = BlizzardAPI()
        self.profile_manager = ProfileManager()
        self.llm = LLMInterface()
        self.logger = get_logger(__name__)
        self.memory = self._load_memory()
        self._last_request_time = 0
        self._request_count = 0

    async def process_request(self, query: str) -> Dict[str, Any]:
        """
        Procesa una petición del usuario y decide qué acción tomar.
        
        Args:
            query: Consulta o instrucción del usuario.
            
        Returns:
            Dict con el resultado de la operación.
        """
        try:
            # Analiza la consulta con el LLM
            intent = await self.llm.analyze_intent(query)
            
            if not self._validate_operation(intent):
                raise PermissionError(f"Operación no permitida: {intent.get('operation')}")

            if intent.get('requires_api_call'):
                return await self._handle_api_request(intent)
            elif intent.get('requires_file_access'):
                return await self._handle_file_operation(intent)
            else:
                return await self._handle_local_query(intent)

        except Exception as e:
            self.logger.error(f"Error procesando la consulta: {e}")
            return {'error': str(e), 'status': 'failed'}

    async def _handle_api_request(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja peticiones a la API de Blizzard.
        
        Args:
            intent: Diccionario con la intención y parámetros de la petición.
            
        Returns:
            Resultado de la petición a la API.
        """
        if not self._can_make_request():
            raise RuntimeError("Límite de peticiones alcanzado")

        try:
            response = await self.blizzard_api.fetch_auction_data()
            if response:
                self._update_memory(intent, response)
            return response or {'error': 'No se obtuvieron datos'}

        except Exception as e:
            self.logger.error(f"Error en petición a API: {e}")
            return {'error': str(e)}

    async def _handle_file_operation(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja operaciones con archivos locales.
        
        Args:
            intent: Diccionario con la intención y parámetros de la operación.
            
        Returns:
            Resultado de la operación con archivos.
        """
        operation = intent.get('operation')
        file_path = intent.get('file_path')

        if not self._validate_file_access(file_path):
            raise PermissionError(f"Acceso denegado al archivo: {file_path}")

        try:
            if operation == "read":
                return self._read_file(file_path)
            elif operation == "write":
                return self._write_file(file_path, intent.get('data'))
            else:
                raise ValueError(f"Operación de archivo no soportada: {operation}")

        except Exception as e:
            self.logger.error(f"Error en operación de archivo: {e}")
            return {'error': str(e)}

    def _can_make_request(self) -> bool:
        """
        Verifica si se puede hacer una nueva petición según los límites configurados.
        
        Returns:
            bool: True si se puede hacer la petición, False en caso contrario.
        """
        current_time = time.time()
        if current_time - self._last_request_time >= 60:  # Reset counter after 1 minute
            self._request_count = 0
            self._last_request_time = current_time

        if self._request_count >= self.config.max_requests_per_minute:
            return False

        self._request_count += 1
        return True

    def _validate_operation(self, intent: Dict[str, Any]) -> bool:
        """
        Valida si una operación está permitida según la configuración.
        
        Args:
            intent: Diccionario con la intención y tipo de operación.
            
        Returns:
            bool: True si la operación está permitida, False en caso contrario.
        """
        if not self.config.allowed_operations:
            return True  # Si no hay restricciones, permite todo

        return intent.get('operation') in self.config.allowed_operations

    def _validate_file_access(self, file_path: str) -> bool:
        """
        Valida si se permite el acceso a un archivo.
        
        Args:
            file_path: Ruta del archivo a validar.
            
        Returns:
            bool: True si se permite el acceso, False en caso contrario.
        """
        if not file_path:
            return False

        # Convertir a Path para manejo seguro de rutas
        path = Path(file_path).resolve()
        
        # Verificar que el archivo está dentro del directorio del proyecto
        project_dir = Path(__file__).parent.parent.resolve()
        return project_dir in path.parents

    def _load_memory(self) -> Dict[str, Any]:
        """
        Carga el archivo de memoria de la IA.
        
        Returns:
            Dict con la memoria cargada o un diccionario vacío si no existe.
        """
        try:
            memory_path = Path(self.config.memory_file)
            if memory_path.exists():
                with open(memory_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error cargando memoria: {e}")
        
        return {}

    def _update_memory(self, intent: Dict[str, Any], result: Dict[str, Any]):
        """
        Actualiza la memoria de la IA con nuevos datos.
        
        Args:
            intent: Intención que generó el resultado.
            result: Resultado de la operación.
        """
        if not self.config.auto_learn:
            return

        try:
            key = self._generate_memory_key(intent)
            self.memory[key] = {
                'result': result,
                'timestamp': time.time(),
                'success_rate': self._calculate_success_rate(intent, result)
            }
            self._save_memory()
        except Exception as e:
            self.logger.error(f"Error actualizando memoria: {e}")

    def _generate_memory_key(self, intent: Dict[str, Any]) -> str:
        """
        Genera una clave única para almacenar en memoria.
        
        Args:
            intent: Intención a partir de la cual generar la clave.
            
        Returns:
            str: Clave única para la memoria.
        """
        return f"{intent.get('operation')}_{intent.get('type')}_{hash(str(intent))}"

    def _calculate_success_rate(self, intent: Dict[str, Any], result: Dict[str, Any]) -> float:
        """
        Calcula la tasa de éxito de una operación.
        
        Args:
            intent: Intención original.
            result: Resultado de la operación.
            
        Returns:
            float: Tasa de éxito entre 0 y 1.
        """
        if 'error' in result:
            return 0.0
        return 1.0  # Implementar lógica más sofisticada según necesidades

    def _save_memory(self):
        """Guarda la memoria en disco."""
        try:
            with open(self.config.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando memoria: {e}")
