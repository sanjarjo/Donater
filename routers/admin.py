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
