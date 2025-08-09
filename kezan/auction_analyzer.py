from typing import List, Dict, Optional
import asyncio
from datetime import datetime
from kezan.llm_interface import LLMInterface
from kezan.blizzard_api import BlizzardAPI
from kezan.profile_manager import ProfileManager, GameVersion
from kezan.realtime_monitor import RealTimeAuctionMonitor, RealTimeMarketAnalyzer

class AuctionAnalyzer:
    def __init__(self):
        self.llm = LLMInterface()
        self.blizzard_api = BlizzardAPI()
        self.profile_manager = ProfileManager()
        self.realtime_monitor = RealTimeAuctionMonitor()
        self.realtime_analyzer = RealTimeMarketAnalyzer(self.realtime_monitor)

    async def analyze_watched_items(self, 
                                  game_version: GameVersion,
                                  realm: str,
                                  use_realtime: bool = True) -> List[Dict]:
        """
        Analiza los items observados para un perfil específico.
        """
        profile = self.profile_manager.get_profile(game_version)
        watched_items = profile.preferences.watched_items
        
        results = []

        # Iniciar monitoreo en tiempo real si no está activo
        if use_realtime and not self.realtime_monitor.is_monitoring:
            asyncio.create_task(self.realtime_monitor.start_monitoring(self.blizzard_api, realm))
        
        for item_id in watched_items:
            if use_realtime:
                # Obtener datos en tiempo real
                current_price_data = self.realtime_monitor.get_current_price(item_id)
                if not current_price_data:
                    continue
                item_data = [current_price_data]
            else:
                # Obtener datos de la API directamente
                current_data = await self.blizzard_api.get_auctions(realm)
                item_data = [
                    auction for auction in current_data 
                    if auction['item']['id'] == item_id
                ]
                if not item_data:
                    continue

            # Obtener historial del item
            history = profile.auction_history.get(item_id, [])
            
            # Analizar oportunidad con LLM
            analysis = await self.llm.analyze_market_opportunity(
                item_data=item_data[0],
                historical_prices=history
            )
            
            results.append({
                'item_id': item_id,
                'current_data': item_data,
                'analysis': analysis
            })

        return results

    async def full_scan(self,
                       game_version: GameVersion,
                       realm: str,
                       scan_interval: int = 300) -> None:
        """
        Realiza un escaneo completo de la casa de subastas.
        
        Args:
            game_version: Versión del juego
            realm: Reino a escanear
            scan_interval: Intervalo entre escaneos en segundos
        """
        while True:
            try:
                profile = self.profile_manager.get_profile(game_version)
                current_data = await self.blizzard_api.get_auctions(realm)

                # Analizar datos con LLM
                opportunities = await self.llm.scan_auction_house(
                    current_data=current_data,
                    profile_preferences=profile.preferences.__dict__,
                    game_version=game_version.value
                )

                # Actualizar historial para items relevantes
                for opp in opportunities:
                    item_id = opp['item_id']
                    self.profile_manager.update_auction_history(
                        game_version,
                        item_id,
                        {
                            'price': opp['price'],
                            'quantity': opp['quantity'],
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    )

                # Esperar hasta el próximo escaneo
                await asyncio.sleep(scan_interval)

            except Exception as e:
                print(f"Error durante el escaneo: {e}")
                await asyncio.sleep(60)  # Esperar un minuto antes de reintentar

    async def get_market_insights(self,
                                game_version: GameVersion,
                                realm: str) -> Dict:
        """
        Obtiene insights del mercado usando el modelo LLM.
        """
        profile = self.profile_manager.get_profile(game_version)
        
        # Obtener datos históricos
        market_trends = []
        for item_id in profile.preferences.watched_items:
            history = profile.auction_history.get(item_id, [])
            if history:
                market_trends.append({
                    'item_id': item_id,
                    'price_history': history[-10:]  # últimos 10 registros
                })

        # Obtener estrategia sugerida
        strategy = self.llm.suggest_search_strategy(
            item_history=market_trends,
            market_trends=market_trends,
            game_version=game_version.value
        )

        return {
            'strategy': strategy,
            'market_trends': market_trends
        }

    async def monitor_price_thresholds(self,
                                     game_version: GameVersion,
                                     realm: str) -> List[Dict]:
        """
        Monitorea los umbrales de precio para items observados.
        """
        profile = self.profile_manager.get_profile(game_version)
        current_data = await self.blizzard_api.get_auctions(realm)
        
        alerts = []
        for item_id, threshold in profile.preferences.price_thresholds.items():
            item_auctions = [
                auction for auction in current_data 
                if auction['item']['id'] == item_id
            ]
            
            if not item_auctions:
                continue

            min_price = min(auction['unit_price'] for auction in item_auctions)
            
            if min_price <= threshold:
                alerts.append({
                    'item_id': item_id,
                    'current_price': min_price,
                    'threshold': threshold,
                    'difference': threshold - min_price
                })

        return alerts
