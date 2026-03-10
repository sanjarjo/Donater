from fastapi import APIRouter
from ..services.order_service import create_order, cancel_order
from fastapi import Request

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/create")
async def create_order_api(request: Request):
    data = await request.json()
    order = create_order(data)
    return {"order_number": order.order_number, "status": order.status}

@router.post("/cancel")
async def cancel_order_api(request: Request):
    data = await request.json()
    result = cancel_order(data["order_id"], data["reason"])
    return result
