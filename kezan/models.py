"""Modelos de datos usados por Kezan Protocol."""

from pydantic import BaseModel


class AuctionItem(BaseModel):
    """Representa un item de subasta analizado."""

    name: str
    ah_price: float
    avg_sell_price: float
    margin: float
