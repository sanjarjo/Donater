# backend/app/routes.py
from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from .models import User, Order
from .utils import create_order_number, get_db

router = APIRouter()

@router.post("/tg_webhook")
async def tg_webhook(req: Request):
    data = await req.json()
    action = data.get("action")
    tg_user = data.get("user")
    payload = data.get("payload", {})

    db: Session = next(get_db())

    # 1️⃣ Ro'yxatdan o'tish
    if action == "register":
        user = db.query(User).filter(User.tg_id==tg_user["id"]).first()
        if not user:
            user = User(tg_id=tg_user["id"], username=tg_user.get("username"))
            db.add(user)
            db.commit()
        return {"status":"ok"}

    # 2️⃣ Zakaz yaratish
    elif action == "create_order":
        user = db.query(User).filter(User.tg_id==tg_user["id"]).first()
        if not user:
            return {"status":"error", "message":"Foydalanuvchi topilmadi"}

        order_number = create_order_number()
        order = Order(
            order_number=order_number,
            user_id=user.id,
            player_id=payload["player_id"],
            zone_id=payload["zone_id"],
            nickname=payload["nickname"],
            diamond=payload["diamond"],
            price=payload["price"]
        )
        db.add(order)
        db.commit()
        # TODO: Adminga xabar yuborish logikasi
        return {"status":"ok", "order_number": order_number}
    
