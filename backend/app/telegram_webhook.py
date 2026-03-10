from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from . import crud, schemas, database
import uuid

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Telegram Mini App webhook
@router.post("/tg_webhook")
async def telegram_webhook(req: Request, db: Session = Depends(get_db)):
    data = await req.json()
    
    user_info = data.get("user")  # {'id': tg_id, 'username': 'user123'}
    action = data.get("action")   # "register" / "create_order"
    payload = data.get("payload") # buyurtma ma'lumotlari

    # Ro'yhatdan o'tish
    if action == "register":
        user_schema = schemas.UserCreate(
            telegram_id=str(user_info['id']),
            username=user_info.get('username','unknown')
        )
        res = crud.create_user(db, user_schema)
        return {"status": "ok", "user_id": res.id}

    # Buyurtma yaratish
    if action == "create_order":
        user = crud.get_user_by_telegram(db, str(user_info['id']))
        if not user:
            return {"status": "error", "detail": "User not found"}
        
        order_schema = schemas.OrderCreate(
            user_id=user.id,
            player_id=payload['player_id'],
            zone_id=payload['zone_id'],
            nickname=payload['nickname'],
            diamond=payload['diamond'],
            price=payload['price']
        )
        order = crud.create_order(db, order_schema)

        # Adminga bildirish (so‘ngra bot orqali yuborish)
        # order.order_number, user.telegram_id, order.nickname, order.diamond, order.price
        # Telegram bot kodida yuboriladi
        
        return {"status": "ok", "order_number": order.order_number}
