from pydantic import BaseModel

class AuctionItem(BaseModel):
    name: str
    ah_price: float
    avg_sell_price: float
    margin: float
