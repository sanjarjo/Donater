from ..database import SessionLocal
from ..models.order import Order
from ..utils.order_id import generate_order_id

def create_order(data: dict):
    db = SessionLocal()
    order = Order(
        order_number=generate_order_id(),
        user_id=data["user_id"],
        player_id=data["player_id"],
        zone_id=data["zone_id"],
        nickname=data["nickname"],
        diamond=data["diamond"],
        price=data["price"],
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()
    return order

def cancel_order(order_id: int, reason: str):
    if len(reason) < 1:
        return {"error": "reason_required"}

    db = SessionLocal()
    order = db.query(Order).get(order_id)
    if not order:
        db.close()
        return {"error": "order_not_found"}

    from ..models.user import User
    user = db.query(User).get(order.user_id)

    order.status = "cancelled"
    order.cancel_reason = reason
    user.balance += order.price

    db.commit()
    db.close()
    return {"status": "cancelled"}
