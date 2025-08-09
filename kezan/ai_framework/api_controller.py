"""Controlador de API para la IA."""

from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime, timedelta
from .memory_manager import ContextMemory
from ..blizzard_api import BlizzardAPI
from ..config import API_CLIENT_ID, API_CLIENT_SECRET

class AIAPIController:
    def __init__(self):
        self.memory = ContextMemory()
        self.blizzard_api = BlizzardAPI()
        self.rate_limits = {
            'auction_house': {
                'calls': 0,
                'reset_time': datetime.now(),
                'limit': 100,  # llamadas
                'window': 60   # segundos
            }
        }

    async def get_auction_data(self, realm: str) -> Optional[Dict]:
        """
        Obtiene datos de la casa de subastas con control de rate limit y memoria contextual.
        """
        # Verificar rate limit
        if not self._check_rate_limit('auction_house'):
            return None

        start_time = time.perf_counter()
        try:
            data = await self.blizzard_api.fetch_auction_data()
            elapsed = time.perf_counter() - start_time
            
            # Registrar la interacción
            self.memory.record_api_interaction(
                'auction_house',
                success=True,
                response_time=elapsed
            )
            
            return data
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            self.memory.record_api_interaction(
                'auction_house',
                success=False,
                response_time=elapsed
            )
            return None

    def _check_rate_limit(self, endpoint: str) -> bool:
        """Verifica y actualiza el rate limit para un endpoint."""
        now = datetime.now()
        limit_info = self.rate_limits[endpoint]
        
        # Reiniciar contador si ha pasado la ventana de tiempo
        if now - limit_info['reset_time'] > timedelta(seconds=limit_info['window']):
            limit_info['calls'] = 0
            limit_info['reset_time'] = now
        
        # Verificar límite
        if limit_info['calls'] >= limit_info['limit']:
            return False
        
        limit_info['calls'] += 1
        return True

    async def analyze_market_data(self, data: Dict) -> Dict:
        """
        Analiza datos del mercado y actualiza patrones en la memoria contextual.
        """
        # Análisis básico de mercado
        analysis = {}
        
        for item_id, auctions in data.items():
            # Calcular estadísticas básicas
            prices = [auction['unit_price'] for auction in auctions]
            if not prices:
                continue
            
            stats = {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': sum(prices) / len(prices),
                'quantity': sum(auction.get('quantity', 1) for auction in auctions)
            }
            
            # Detectar patrones
            pattern = self._detect_market_pattern(stats)
            if pattern:
                self.memory.add_market_pattern(item_id, pattern)
            
            analysis[item_id] = stats
        
        return analysis

    def _detect_market_pattern(self, stats: Dict) -> Optional[Dict]:
        """Detecta patrones en las estadísticas de mercado."""
        pattern = None
        
        # Ejemplo de detección de patrón
        price_spread = stats['max_price'] - stats['min_price']
        if price_spread > stats['avg_price'] * 0.5:  # Alta volatilidad
            pattern = {
                'type': 'high_volatility',
                'spread': price_spread,
                'avg_price': stats['avg_price']
            }
        
        return pattern

    def get_optimal_strategy(self, item_id: int, current_price: int) -> Dict:
        """
        Determina la mejor estrategia basada en la memoria contextual.
        """
        # Obtener patrones históricos
        patterns = self.memory.get_market_patterns(item_id)
        
        # Obtener estrategias similares
        similar_strategies = self.memory.get_similar_strategies({
            'item_id': item_id,
            'price_range': self._get_price_range(current_price)
        })
        
        # Analizar y recomendar estrategia
        strategy = {
            'action': 'hold',  # Por defecto, mantener
            'confidence': 0.0,
            'reasoning': []
        }
        
        if patterns:
            latest_pattern = patterns[0]
            if latest_pattern['type'] == 'high_volatility':
                if current_price < latest_pattern['avg_price']:
                    strategy.update({
                        'action': 'buy',
                        'confidence': 0.7,
                        'reasoning': ['Precio actual bajo el promedio en mercado volátil']
                    })
        
        if similar_strategies:
            # Usar la estrategia más reciente como referencia
            latest_strategy = similar_strategies[0]
            if latest_strategy['success_rate'] > 0.7:
                strategy.update({
                    'action': latest_strategy['action'],
                    'confidence': latest_strategy['success_rate'],
                    'reasoning': [f"Estrategia similar exitosa ({latest_strategy['success_rate']*100:.0f}% tasa de éxito)"]
                })
        
        return strategy

    def _get_price_range(self, price: int) -> str:
        """Categoriza un precio en un rango para comparación de estrategias."""
        ranges = [
            (0, 100, 'very_low'),
            (100, 1000, 'low'),
            (1000, 10000, 'medium'),
            (10000, 100000, 'high'),
            (100000, float('inf'), 'very_high')
        ]
        
        for min_price, max_price, category in ranges:
            if min_price <= price < max_price:
                return category
        
        return 'unknown'
