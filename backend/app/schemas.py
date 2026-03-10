from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    telegram_id: str
    username: str

class OrderCreate(BaseModel):
    user_id: int
    player_id: str
    zone_id: str
    nickname: str
    diamond: int
    price: int

class OrderCancel(BaseModel):
    order_id: int
    reason: str
