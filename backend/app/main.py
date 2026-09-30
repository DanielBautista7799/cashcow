
from fastapi import FastAPI

from app.routers import atm, service_call, auth, branches

app = FastAPI(
    title = "CashCow ATM command center",
    description="ATM branch management API",
    version="0.2.0"
)

app.include_router(atm.router)
app.include_router(service_call.router)
app.include_router(auth.router)
app.include_router(branches.router)
