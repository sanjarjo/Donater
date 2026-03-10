from fastapi import FastAPI
from .routers import auth, orders

app = FastAPI(title="MLBB TopUp Backend")

app.include_router(auth.router)
app.include_router(orders.router)
