import pytest
from kezan.auction_analyzer import AuctionAnalyzer
from kezan.profile_manager import GameVersion

@pytest.mark.asyncio
async def test_analyze_watched_items():
    analyzer = AuctionAnalyzer()
    game_version = GameVersion.RETAIL
    realm = "test-realm"

    # Simular datos de prueba
    result = await analyzer.analyze_watched_items(game_version, realm, use_realtime=False)

    # Validar que el resultado sea una lista
    assert isinstance(result, list)

    # Validar que cada elemento tenga las claves esperadas
    for item in result:
        assert "item_id" in item
        assert "current_data" in item
        assert "analysis" in item
