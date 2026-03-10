from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram(db, user.telegram_id)
    if db_user:
        return {"status": "already exists"}
    crud.create_user(db, user)
    return {"status": "ok"}

@app.get("/orders/user/{telegram_id}")
def user_orders(telegram_id: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_telegram(db, telegram_id)
    if not user:
        return []
    return crud.get_orders_for_user(db, user.id)

@app.get("/orders")
def all_orders(db: Session = Depends(get_db)):
    return crud.get_all_orders(db)

@app.post("/orders/cancel")
def cancel(order: schemas.OrderCancel, db: Session = Depends(get_db)):
    res = crud.cancel_order(db, order.order_id, order.reason)
    if not res:
        return {"status": "error"}
    return {"status": "ok"}
