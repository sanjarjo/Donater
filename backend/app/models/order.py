from sqlalchemy import Column, Integer, String
from ..database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True)
    user_id = Column(Integer)
    player_id = Column(String)
    zone_id = Column(String)
    nickname = Column(String)
    diamond = Column(Integer)
    price = Column(Integer)
    status = Column(String, default="pending")  # pending, processing, completed, cancelled
    cancel_reason = Column(String, nullable=True)
