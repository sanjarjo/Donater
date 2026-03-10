from sqlalchemy.orm import Session
from . import models, schemas
import uuid

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(telegram_id=user.telegram_id, username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_telegram(db: Session, telegram_id: str):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def create_order(db: Session, order: schemas.OrderCreate):
    order_number = str(uuid.uuid4())[:8]
    db_order = models.Order(
        order_number=order_number,
        user_id=order.user_id,
        player_id=order.player_id,
        zone_id=order.zone_id,
        nickname=order.nickname,
        diamond=order.diamond,
        price=order.price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def cancel_order(db: Session, order_id: int, reason: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None
    order.status = "canceled"
    order.cancel_reason = reason
    db.commit()
    db.refresh(order)
    return order

def get_orders_for_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def get_all_orders(db: Session):
    return db.query(models.Order).all()
