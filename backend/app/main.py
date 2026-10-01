
from fastapi import FastAPI

from app.routers import atm, service_call, auth, branches
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title = "CashCow ATM command center",
    description="ATM branch management API",
    version="0.2.0"
)

app.include_router(atm.router)
app.include_router(service_call.router)
app.include_router(auth.router)
app.include_router(branches.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)