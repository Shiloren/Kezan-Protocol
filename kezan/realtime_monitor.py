from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass

@dataclass
class RealTimeAuctionData:
    timestamp: datetime
    item_id: int
    current_price: int
    quantity: int
    is_buyout: bool
    time_left: str

class RealTimeAuctionMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_data: Dict[int, List[RealTimeAuctionData]] = {}
        self.last_update: Optional[datetime] = None
        self.is_monitoring = False
        self.update_interval = 60  # segundos (ajustable según la API de Blizzard)

    async def start_monitoring(self, blizzard_api, realm: str):
        """Inicia el monitoreo en tiempo real de la casa de subastas."""
        self.is_monitoring = True
        while self.is_monitoring:
            try:
                await self.update_auction_data(blizzard_api, realm)
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Error en monitoreo: {e}")
                await asyncio.sleep(5)  # Breve espera antes de reintentar

    async def stop_monitoring(self):
        """Detiene el monitoreo en tiempo real."""
        self.is_monitoring = False

    async def update_auction_data(self, blizzard_api, realm: str):
        """Actualiza los datos de subasta en tiempo real."""
        try:
            raw_data = await blizzard_api.get_auctions(realm)
            self.last_update = datetime.now()
            
            # Limpiar datos antiguos
            self.current_data.clear()
            
            # Procesar nuevos datos
            for auction in raw_data:
                item_id = auction['item']['id']
                auction_data = RealTimeAuctionData(
                    timestamp=self.last_update,
                    item_id=item_id,
                    current_price=auction['unit_price'],
                    quantity=auction.get('quantity', 1),
                    is_buyout=auction.get('buyout', 0) > 0,
                    time_left=auction.get('time_left', 'UNKNOWN')
                )
                
                if item_id not in self.current_data:
                    self.current_data[item_id] = []
                self.current_data[item_id].append(auction_data)

            self.logger.info(f"Datos actualizados para {len(self.current_data)} items")
            return True

        except Exception as e:
            self.logger.error(f"Error actualizando datos: {e}")
            return False

    def get_current_price(self, item_id: int) -> Optional[Dict]:
        """Obtiene el precio actual más bajo para un item."""
        if item_id not in self.current_data:
            return None

        current_auctions = self.current_data[item_id]
        if not current_auctions:
            return None

        lowest_price = min(auction.current_price for auction in current_auctions)
        relevant_auctions = [
            auction for auction in current_auctions 
            if auction.current_price == lowest_price
        ]

        return {
            'price': lowest_price,
            'quantity': sum(auction.quantity for auction in relevant_auctions),
            'timestamp': self.last_update.isoformat(),
            'time_left': relevant_auctions[0].time_left
        }

    def get_market_snapshot(self, item_ids: List[int]) -> Dict:
        """Obtiene un snapshot del mercado para una lista de items."""
        snapshot = {}
        current_time = datetime.now()

        for item_id in item_ids:
            if item_id in self.current_data:
                auctions = self.current_data[item_id]
                prices = [auction.current_price for auction in auctions]
                
                snapshot[item_id] = {
                    'lowest_price': min(prices),
                    'highest_price': max(prices),
                    'available_quantity': sum(auction.quantity for auction in auctions),
                    'num_auctions': len(auctions),
                    'timestamp': self.last_update.isoformat(),
                    'age_seconds': (current_time - self.last_update).total_seconds()
                }

        return snapshot

class RealTimeMarketAnalyzer:
    def __init__(self, monitor: RealTimeAuctionMonitor):
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)

    async def analyze_item(self, 
                         item_id: int, 
                         historical_data: List[Dict],
                         llm_interface) -> Dict:
        """
        Analiza un item combinando datos en tiempo real con históricos.
        """
        current_data = self.monitor.get_current_price(item_id)
        if not current_data:
            return {"error": "No hay datos actuales disponibles"}

        # Preparar datos para el LLM
        analysis_data = {
            "current_market": current_data,
            "historical_context": historical_data[-10:] if historical_data else [],  # Últimos 10 registros
            "market_age_seconds": (datetime.now() - self.monitor.last_update).total_seconds()
        }

        # Obtener análisis del LLM
        prompt = self._build_analysis_prompt(analysis_data)
        analysis = await llm_interface.analyze_market_opportunity(prompt)

        return {
            "timestamp": datetime.now().isoformat(),
            "current_data": current_data,
            "analysis": analysis,
            "data_freshness": "real_time" if analysis_data["market_age_seconds"] < 300 else "stale"
        }

    def _build_analysis_prompt(self, data: Dict) -> str:
        """Construye un prompt optimizado para el análisis en tiempo real."""
        return f"""Analiza la siguiente oportunidad de mercado:

Datos actuales del mercado:
{data['current_market']}

Contexto histórico reciente:
{data['historical_context']}

Edad de los datos: {data['market_age_seconds']} segundos

Proporciona un análisis que incluya:
1. Evaluación del precio actual vs tendencia histórica
2. Oportunidad inmediata de mercado
3. Recomendación de acción a corto plazo (próximos minutos)
4. Riesgo asociado con la acción recomendada

El análisis debe enfocarse en la acción inmediata dado que los datos son en tiempo real.
"""
