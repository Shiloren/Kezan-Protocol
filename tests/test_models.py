"""Pruebas para los modelos de datos."""

from kezan.models import AuctionItem


def test_auction_item_model():
    """Crea una instancia y verifica sus atributos."""
    item = AuctionItem(name="Poción", ah_price=1.0, avg_sell_price=2.0, margin=0.5)
    assert item.name == "Poción"
    assert item.margin == 0.5
