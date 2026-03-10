from fastapi import APIRouter
from fastapi import Request
from ..database import SessionLocal
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user(request: Request):
    data = await request.json()
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == data["telegram_id"]).first()
    if user:
        db.close()
        return {"status": "exists"}

    new_user = User(
        telegram_id=data["telegram_id"],
        username=data.get("username", "")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"status": "ok", "user_id": new_user.id}
