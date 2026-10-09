from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models.atm import Atm
from app.models.enums import AtmStatus, UserRole
from app.models.user import User
from app.pagination import PageParams
from app.schemas.atm import AtmCreate, AtmRead
from app.schemas.page import Page


router = APIRouter(prefix="/atms", tags=["atms"])


SORT_COLUMNS = {
    "id": Atm.id,
    "serial_number": Atm.serial_number,
    "model": Atm.model,
    "status": Atm.status,
    "cash_level": Atm.cash_level,
    "branch_id": Atm.branch_id,
}


@router.get("", response_model=Page[AtmRead])
async def list_atms(
    pagination: PageParams = Depends(),
    max_cash: Decimal | None = Query(
        default=None,
        ge=0,
        le=100,
    ),
    status_filter: AtmStatus | None = Query(
        default=None,
        alias="status",
    ),
    branch_id: int | None = Query(
        default=None,
        ge=1,
    ),
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if pagination.sort_by not in SORT_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid sort field",
        )

    conditions = [
        Atm.status != AtmStatus.OFFLINE
    ]

    if max_cash is not None:
        conditions.append(
            Atm.cash_level < max_cash
        )

    if status_filter is not None:
        conditions.append(
            Atm.status == status_filter
        )

    if branch_id is not None:
        conditions.append(
            Atm.branch_id == branch_id
        )

    if search:
        search_value = f"%{search}%"
        conditions.append(
            or_(
                Atm.model.ilike(search_value),
                Atm.serial_number.ilike(search_value),
            )
        )

    count_statement = (
        select(func.count())
        .select_from(Atm)
        .where(*conditions)
    )

    total = (
        await db.execute(count_statement)
    ).scalar_one()

    sort_column = SORT_COLUMNS[
        pagination.sort_by
    ]

    if pagination.sort_dir == "desc":
        order = sort_column.desc()
    else:
        order = sort_column.asc()

    statement = (
        select(Atm)
        .where(*conditions)
        .order_by(order)
        .offset(pagination.offset)
        .limit(pagination.size)
    )

    result = await db.execute(statement)

    return {
        "items": list(result.scalars().all()),
        "total": total,
    }


@router.post(
    "",
    response_model=AtmRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_atm(
    payload: AtmCreate,
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
):
    atm = Atm(**payload.model_dump())

    db.add(atm)
    await db.commit()
    await db.refresh(atm)

    return atm
