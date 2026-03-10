from fastapi import APIRouter
from ..services.order_service import create_order

router = APIRouter()

@router.post("/order/create")
def create(data: dict):

    order = create_order(data)

    return {
        "status": "success",
        "order_id": order.order_number
    }
