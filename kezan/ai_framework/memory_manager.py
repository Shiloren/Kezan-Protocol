"""Gestión de memoria contextual para la IA."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

class ContextMemory:
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.expanduser("~/.kezan/ai_memory")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_context = {}
        self._load_memory()

    def _load_memory(self):
        """Carga la memoria contextual desde el disco."""
        memory_file = self.storage_path / "context_memory.json"
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                self.current_context = json.load(f)

    def save_memory(self):
        """Guarda la memoria contextual en disco."""
        memory_file = self.storage_path / "context_memory.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_context, f, indent=2)

    def add_market_pattern(self, item_id: int, pattern: Dict):
        """Añade un patrón de mercado identificado."""
        if 'market_patterns' not in self.current_context:
            self.current_context['market_patterns'] = {}
        
        if str(item_id) not in self.current_context['market_patterns']:
            self.current_context['market_patterns'][str(item_id)] = []
        
        pattern['timestamp'] = datetime.now().isoformat()
        self.current_context['market_patterns'][str(item_id)].append(pattern)
        self.save_memory()

    def get_market_patterns(self, item_id: int) -> List[Dict]:
        """Recupera patrones de mercado para un item específico."""
        patterns = self.current_context.get('market_patterns', {}).get(str(item_id), [])
        return sorted(patterns, key=lambda x: x['timestamp'], reverse=True)

    def add_successful_strategy(self, strategy: Dict):
        """Registra una estrategia exitosa."""
        if 'successful_strategies' not in self.current_context:
            self.current_context['successful_strategies'] = []
        
        strategy['timestamp'] = datetime.now().isoformat()
        self.current_context['successful_strategies'].append(strategy)
        self.save_memory()

    # Alias conveniente para los tests/llamadas que hablan de "estrategias similares"
    def add_similar_strategy(self, strategy: Dict):
        """Agrega una estrategia considerada similar (se guarda como exitosa).

        Este método es un alias semántico de add_successful_strategy para mantener
        compatibilidad con llamadas que registran estrategias similares previas.
        """
        self.add_successful_strategy(strategy)

    def get_similar_strategies(self, conditions: Dict) -> List[Dict]:
        """Busca estrategias similares basadas en condiciones dadas."""
        strategies = self.current_context.get('successful_strategies', [])
        
        # Filtrar estrategias basadas en similitud
        similar = []
        for strategy in strategies:
            if all(strategy.get(k) == v for k, v in conditions.items()):
                similar.append(strategy)
        
        return sorted(similar, key=lambda x: x['timestamp'], reverse=True)

    def record_api_interaction(self, endpoint: str, success: bool, response_time: float):
        """Registra interacciones con la API para optimización."""
        if 'api_interactions' not in self.current_context:
            self.current_context['api_interactions'] = {}
        
        if endpoint not in self.current_context['api_interactions']:
            self.current_context['api_interactions'][endpoint] = {
                'success_count': 0,
                'failure_count': 0,
                'average_response_time': 0,
                'last_update': None
            }
        
        stats = self.current_context['api_interactions'][endpoint]
        if success:
            stats['success_count'] += 1
        else:
            stats['failure_count'] += 1
        
        # Actualizar tiempo de respuesta promedio
        total = stats['success_count'] + stats['failure_count']
        stats['average_response_time'] = (
            (stats['average_response_time'] * (total - 1) + response_time) / total
        )
        stats['last_update'] = datetime.now().isoformat()
        self.save_memory()

    def get_api_performance(self, endpoint: str) -> Optional[Dict]:
        """Obtiene estadísticas de rendimiento para un endpoint específico."""
        return self.current_context.get('api_interactions', {}).get(endpoint)
