from typing import List, Dict, Optional
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging

class MarketDataProcessor:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def preprocess_auction_data(self, raw_data: List[Dict]) -> Dict:
        """
        Pre-procesa los datos de subasta para reducir la carga en el LLM.
        """
        processed = {
            'summary': {},
            'trends': {},
            'anomalies': []
        }

        try:
            # Calcular estadísticas básicas por item
            item_stats = {}
            for auction in raw_data:
                item_id = auction['item']['id']
                price = auction['unit_price']
                
                if item_id not in item_stats:
                    item_stats[item_id] = {
                        'prices': [],
                        'count': 0,
                        'total_quantity': 0
                    }
                
                item_stats[item_id]['prices'].append(price)
                item_stats[item_id]['count'] += 1
                item_stats[item_id]['total_quantity'] += auction.get('quantity', 1)

            # Calcular métricas y detectar anomalías
            for item_id, stats in item_stats.items():
                prices = np.array(stats['prices'])
                
                # Estadísticas básicas
                processed['summary'][item_id] = {
                    'min_price': float(np.min(prices)),
                    'max_price': float(np.max(prices)),
                    'mean_price': float(np.mean(prices)),
                    'median_price': float(np.median(prices)),
                    'std_price': float(np.std(prices)),
                    'total_listings': stats['count'],
                    'total_quantity': stats['total_quantity']
                }

                # Detección de anomalías (precios que se desvían significativamente)
                z_scores = np.abs((prices - np.mean(prices)) / np.std(prices))
                anomaly_indices = np.where(z_scores > 3)[0]
                
                if len(anomaly_indices) > 0:
                    processed['anomalies'].extend([
                        {
                            'item_id': item_id,
                            'price': float(prices[i]),
                            'z_score': float(z_scores[i])
                        }
                        for i in anomaly_indices
                    ])

            return processed
        except Exception as e:
            self.logger.error(f"Error preprocessing auction data: {e}")
            return None

    def cache_results(self, key: str, data: Dict, ttl_minutes: int = 15):
        """
        Cachea resultados procesados para reducir carga en el LLM.
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        cache_data = {
            'data': data,
            'expires': (datetime.now() + timedelta(minutes=ttl_minutes)).isoformat()
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

    def get_cached_results(self, key: str) -> Optional[Dict]:
        """
        Recupera resultados cacheados si son válidos.
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            expires = datetime.fromisoformat(cache_data['expires'])
            
            if datetime.now() > expires:
                return None

            return cache_data['data']
        except Exception as e:
            self.logger.error(f"Error reading cache: {e}")
            return None

class LLMOptimizer:
    def __init__(self, max_tokens_per_request: int = 1000):
        self.max_tokens = max_tokens_per_request
        self.context_memory = {}
        self.logger = logging.getLogger(__name__)

    def chunk_market_data(self, data: Dict) -> List[Dict]:
        """
        Divide datos grandes en chunks procesables.
        """
        chunks = []
        current_chunk = {'items': []}
        current_size = 0
        
        for item_id, stats in data.get('summary', {}).items():
            item_data = {'id': item_id, **stats}
            estimated_tokens = len(str(item_data)) // 4  # Estimación aproximada
            
            if current_size + estimated_tokens > self.max_tokens:
                chunks.append(current_chunk)
                current_chunk = {'items': []}
                current_size = 0
            
            current_chunk['items'].append(item_data)
            current_size += estimated_tokens
        
        if current_chunk['items']:
            chunks.append(current_chunk)
        
        return chunks

    def optimize_prompt(self, prompt: str, context: Dict) -> str:
        """
        Optimiza el prompt para el LLM considerando el contexto.
        """
        # Extraer información relevante del contexto
        relevant_context = self._extract_relevant_context(prompt, context)
        
        # Construir prompt optimizado
        optimized = f"""Analiza los siguientes datos del mercado:
Contexto previo relevante: {json.dumps(relevant_context, indent=2)}

Datos actuales:
{prompt}

Proporciona un análisis considerando:
1. Tendencias de precios
2. Anomalías detectadas
3. Oportunidades de mercado
4. Recomendaciones de acción

Formato: Responde en JSON con las siguientes claves:
{
    "analysis": string,
    "opportunities": array,
    "risks": array,
    "actions": array
}
"""
        return optimized

    def _extract_relevant_context(self, prompt: str, context: Dict) -> Dict:
        """
        Extrae contexto relevante para el prompt actual.
        """
        relevant = {}
        
        # Identificar items mencionados en el prompt
        mentioned_items = self._find_mentioned_items(prompt)
        
        # Extraer historial relevante
        for item_id in mentioned_items:
            if item_id in context:
                relevant[item_id] = {
                    'recent_trends': context[item_id].get('trends', [])[-5:],
                    'last_analysis': context[item_id].get('last_analysis'),
                    'price_thresholds': context[item_id].get('thresholds')
                }
        
        return relevant

    def _find_mentioned_items(self, prompt: str) -> List[str]:
        """
        Identifica items mencionados en el prompt.
        """
        # Implementar lógica de extracción de IDs de items
        # Por ahora, una implementación simple
        import re
        return list(set(re.findall(r'item_id["\']:\s*(\d+)', prompt)))

    def update_context_memory(self, item_id: str, analysis_result: Dict):
        """
        Actualiza la memoria de contexto con nuevos resultados.
        """
        if item_id not in self.context_memory:
            self.context_memory[item_id] = {
                'trends': [],
                'analyses': []
            }
        
        # Mantener solo los últimos 10 análisis
        self.context_memory[item_id]['analyses'].append({
            'timestamp': datetime.now().isoformat(),
            'result': analysis_result
        })
        self.context_memory[item_id]['analyses'] = self.context_memory[item_id]['analyses'][-10:]

class FallbackStrategy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_fallback_analysis(self, data: Dict) -> Dict:
        """
        Proporciona análisis básico cuando el LLM está sobrecargado.
        """
        try:
            summary = data.get('summary', {})
            analysis = {
                'basic_stats': {},
                'simple_recommendations': []
            }

            for item_id, stats in summary.items():
                # Análisis básico basado en estadísticas
                price_range = stats['max_price'] - stats['min_price']
                price_volatility = stats['std_price'] / stats['mean_price'] if stats['mean_price'] > 0 else 0
                
                analysis['basic_stats'][item_id] = {
                    'price_range': price_range,
                    'volatility': price_volatility,
                    'market_activity': stats['total_listings']
                }

                # Recomendaciones simples basadas en reglas
                if price_volatility > 0.2:  # Alta volatilidad
                    analysis['simple_recommendations'].append({
                        'item_id': item_id,
                        'type': 'high_volatility',
                        'message': 'Precaución: Alta volatilidad de precios'
                    })

                if stats['total_listings'] < 5:  # Mercado poco líquido
                    analysis['simple_recommendations'].append({
                        'item_id': item_id,
                        'type': 'low_liquidity',
                        'message': 'Mercado con poca liquidez'
                    })

            return analysis
        except Exception as e:
            self.logger.error(f"Error in fallback analysis: {e}")
            return {
                'error': 'No se pudo completar el análisis',
                'timestamp': datetime.now().isoformat()
            }
