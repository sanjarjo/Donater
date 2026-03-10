from fastapi import APIRouter
from ..database import SessionLocal
from ..models.order import Order

router = APIRouter()

@router.post("/admin/order/complete")
def complete(order_id:int):

    db = SessionLocal()

    order = db.query(Order).get(order_id)

    order.status = "completed"

    db.commit()

    return {"status":"ok"}

@router.post("/admin/order/cancel")
def cancel(order_id:int, reason:str):

    if len(reason) < 1:
        return {"error":"reason_required"}

    db = SessionLocal()

    order = db.query(Order).get(order_id)

    order.status = "cancelled"

    order.cancel_reason = reason

    db.commit()

    return {"status":"cancelled"}
