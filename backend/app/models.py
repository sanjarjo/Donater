from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String)
    balance = Column(Integer, default=0)
    role = Column(String, default="USER")  # USER / ADMIN / SUPER_ADMIN

    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    player_id = Column(String)
    zone_id = Column(String)
    nickname = Column(String)
    diamond = Column(Integer)
    price = Column(Integer)
    status = Column(String, default="pending")  # pending / completed / canceled
    cancel_reason = Column(String, nullable=True)

    user = relationship("User", back_populates="orders")
