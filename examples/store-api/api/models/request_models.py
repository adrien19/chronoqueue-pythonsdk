from pydantic import BaseModel
from typing import List, Dict


class Item(BaseModel):
    name: str
    quantity: int
    price: float


class CartItems(BaseModel):
    items: List[Item]
