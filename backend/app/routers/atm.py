





from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select

from app.schemas.atm import AtmCreate, AtmRead
from app.dependencies import get_current_user, get_db, require_role
from app.models.atm import Atm
from app.models.enums import AtmStatus, UserRole
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


router = APIRouter(prefix="/equipment", tags=["equipment"])

@router.get("", response_model=list[AtmRead])
async def list_atms(max_cash: Decimal | None = Query(
    default=None,
    ge=0,
    le=100,
    description="Only return atms lower than this cash percentage"
), current_user: User=Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[Atm]:
    statement = select(Atm).where(Atm.status != AtmStatus.OFFLINE)

    if max_cash is not None:
        statement = statement.where(Atm.cash_level < max_cash)
    statement = statement.order_by(Atm.id)

    result = await db.execute(statement)
    return list(result.scalars().all())

#payload means that the user must send a response in the JSON format so ti can be stored in payload
@router.post(path="", response_model=AtmRead, status_code= status.HTTP_201_CREATED)
async def create_equipment(payload: AtmCreate,current_user: User = Depends(
    require_role(UserRole.ADMIN)
), db: AsyncSession = Depends(get_db)):
    #** spreads it across the equpment argumanets .modeldump turns the pydantic obj and turns it into python
    """ same as 
    Equipment(
    serial_number=payload.serial_number,
    model=payload.model,
    status=payload.status,
    charge_level=payload.charge_level,
    facility_id=payload.facility_id
)"""
    equipment = Atm(**payload.model_dump())
    #no need to be waited on just a stage 
    db.add(equipment)
    await db.commit()
    #update so it appears
    await db.refresh(equipment)

    return equipment

