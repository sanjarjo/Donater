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
mini app ishlatish bosilganda foydalanuvchi username va tg id si bilan ro'yhatdan otishi va pastda panellar bo'lishi kerak misol asosiy, hamyon sozlamalar , va h.k buyurtma berish birinchi miqdor korsatiladi va yonida kichik uchburchak bo'ladi va tanlangan pakat haqida batafsil malumot bo'ladi bosilganda undan keyin id zona id va tekshiruvlar va zakaz berish pastda buyurtmalarim paneli(menyusi) bosilganda buyurtma haqidagi to'liq malumot boladi va holati va barcha buyurtmalar tarixi bo'ladi va admin zakaz haqida malumot oladi va holatini o'zgartirish shu funk siyalar ham bolsin      shularni barchasini saytga aylantirib yuboramizmi a
    if len(reason) < 1:
        return {"error":"reason_required"}

    db = SessionLocal()

    order = db.query(Order).get(order_id)

    order.status = "cancelled"

    order.cancel_reason = reason

    db.commit()

    return {"status":"cancelled"}

from ..models.user import User

user = db.query(User).get(order.user_id)

user.balance += order.price
