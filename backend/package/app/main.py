import asyncio
import boto3
from fastapi import FastAPI, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import atm, service_call, auth, branches
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.dependencies import get_db, require_role
from app.models.enums import UserRole

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
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

@app.get("/health/ready", tags=["health"])
async def healthready(db: AsyncSession = Depends(get_db)):
        statement = select(1)
        try:
            await db.execute(statement)
            return {"status":"ready"}
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable"            
                )
        

@app.get("/health/detail", tags=["health"])
async def healthdetail(db: AsyncSession = Depends(get_db), current_user = Depends(require_role(UserRole.ADMIN))):
    database_status = "ok"
    s3_status = "ok"

    try:
        statement = select(1)
        await db.execute(statement)
    except Exception:
        database_status = "unavailable"

    try:
        s3_client = boto3.client("s3")
        await asyncio.wait_for(
            asyncio.to_thread(
                    s3_client.head_bucket,
                Bucket="cashcow-diagnostic-reports-2478"
            ),
            timeout=3
        )
    except Exception:
        s3_status = "unavailable"

    return {
        "database": database_status,
        "s3": s3_status
    }