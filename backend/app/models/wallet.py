from sqlalchemy import Column, Integer, ForeignKey
from ..database import Base

class Wallet(Base):

    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    balance = Column(Integer, default=0)
