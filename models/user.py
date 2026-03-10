from sqlalchemy import Column, Integer, String
from ..database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    telegram_id = Column(String, unique=True)

    username = Column(String)

    balance = Column(Integer, default=0)
