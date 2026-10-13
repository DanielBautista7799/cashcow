from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_db,
    require_permission,
)
from app.models.atm import Atm
from app.models.audit_entry import AuditEntry
from app.models.enums import AtmStatus
from app.models.user import User
from app.pagination import PageParams
from app.permissions import (
    Permission,
    permissions_for_role,
)
from app.schemas.atm import (
    AtmCreate,
    AtmRead,
    AtmUpdate,
)
from app.schemas.audit import AuditEntryRead
from app.schemas.page import Page
from app.services.operations import (
    create_atm as create_atm_record,
    restore_atm,
    soft_delete_atm,
    update_atm,
)


router = APIRouter(
    prefix="/atms",
    tags=["atms"],
)


SORT_COLUMNS = {
    "id": Atm.id,
    "serial_number": Atm.serial_number,
    "model": Atm.model,
    "status": Atm.status,
    "cash_level": Atm.cash_level,
    "branch_id": Atm.branch_id,
}


@router.get(
    "",
    response_model=Page[AtmRead],
)
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
    current_user: User = Depends(
        require_permission(
            Permission.ASSET_READ
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    if pagination.sort_by not in SORT_COLUMNS:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail="Invalid sort field",
        )

    conditions = [
        Atm.is_active.is_(True),
        Atm.status != AtmStatus.OFFLINE,
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
                Atm.model.ilike(
                    search_value
                ),
                Atm.serial_number.ilike(
                    search_value
                ),
            )
        )

    count_statement = (
        select(func.count())
        .select_from(Atm)
        .where(*conditions)
    )

    total = (
        await db.execute(
            count_statement
        )
    ).scalar_one()

    sort_column = SORT_COLUMNS[
        pagination.sort_by
    ]

    order = (
        sort_column.desc()
        if pagination.sort_dir == "desc"
        else sort_column.asc()
    )

    statement = (
        select(Atm)
        .where(*conditions)
        .order_by(order)
        .offset(pagination.offset)
        .limit(pagination.size)
    )

    result = await db.execute(
        statement
    )

    return {
        "items": list(
            result.scalars().all()
        ),
        "total": total,
    }


@router.get(
    "/inactive",
    response_model=list[AtmRead],
)
async def list_inactive_atms(
    _: User = Depends(
        require_permission(
            Permission.ASSET_WRITE
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Atm)
        .where(
            Atm.is_active.is_(False)
        )
        .order_by(Atm.id)
    )

    return list(
        result.scalars().all()
    )


@router.post(
    "",
    response_model=AtmRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_atm(
    payload: AtmCreate,
    current_user: User = Depends(
        require_permission(
            Permission.ASSET_WRITE
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    return await create_atm_record(
        db,
        payload.model_dump(),
        current_user,
    )


@router.get(
    "/{atm_id}",
    response_model=AtmRead,
)
async def get_atm(
    atm_id: int,
    _: User = Depends(
        require_permission(
            Permission.ASSET_READ
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Atm).where(
            Atm.id == atm_id,
            Atm.is_active.is_(True),
        )
    )

    atm = result.scalar_one_or_none()

    if atm is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="ATM not found",
        )

    return atm


@router.patch(
    "/{atm_id}",
    response_model=AtmRead,
)
async def patch_atm(
    atm_id: int,
    payload: AtmUpdate,
    current_user: User = Depends(
        require_permission(
            Permission.ASSET_WRITE
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Atm).where(
            Atm.id == atm_id,
            Atm.is_active.is_(True),
        )
    )

    atm = result.scalar_one_or_none()

    if atm is None:
        raise HTTPException(
            status_code=404,
            detail="ATM not found",
        )

    values = payload.model_dump(
        exclude_unset=True
    )

    if any(
        value is None
        for value in values.values()
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "ATM update fields "
                "cannot be null"
            ),
        )

    return await update_atm(
        db,
        atm,
        values,
        current_user,
    )


@router.delete(
    "/{atm_id}",
    response_model=AtmRead,
)
async def delete_atm(
    atm_id: int,
    current_user: User = Depends(
        require_permission(
            Permission.ASSET_WRITE
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Atm).where(
            Atm.id == atm_id,
            Atm.is_active.is_(True),
        )
    )

    atm = result.scalar_one_or_none()

    if atm is None:
        raise HTTPException(
            status_code=404,
            detail="ATM not found",
        )

    return await soft_delete_atm(
        db,
        atm,
        current_user,
    )


@router.post(
    "/{atm_id}/restore",
    response_model=AtmRead,
)
async def restore_deleted_atm(
    atm_id: int,
    current_user: User = Depends(
        require_permission(
            Permission.ASSET_WRITE
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Atm).where(
            Atm.id == atm_id,
            Atm.is_active.is_(False),
        )
    )

    atm = result.scalar_one_or_none()

    if atm is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Inactive ATM not found"
            ),
        )

    return await restore_atm(
        db,
        atm,
        current_user,
    )


@router.get(
    "/{atm_id}/history",
    response_model=list[AuditEntryRead],
)
async def get_atm_history(
    atm_id: int,
    current_user: User = Depends(
        require_permission(
            Permission.AUDIT_READ
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    atm = await db.get(
        Atm,
        atm_id,
    )

    if atm is None:
        raise HTTPException(
            status_code=404,
            detail="ATM not found",
        )

    permissions = permissions_for_role(
        current_user.role
    )

    if (
        not atm.is_active
        and Permission.ASSET_WRITE
        not in permissions
    ):
        raise HTTPException(
            status_code=404,
            detail="ATM not found",
        )

    statement = (
        select(
            AuditEntry.id,
            AuditEntry.record_type,
            AuditEntry.record_id,
            AuditEntry.action,
            AuditEntry.acting_user_id,
            User.username.label(
                "acting_username"
            ),
            AuditEntry.created_at,
            AuditEntry.changes,
        )
        .join(
            User,
            User.id
            == AuditEntry.acting_user_id,
        )
        .where(
            AuditEntry.record_type
            == "atm",
            AuditEntry.record_id
            == atm_id,
        )
        .order_by(
            AuditEntry.created_at.asc(),
            AuditEntry.id.asc(),
        )
    )

    result = await db.execute(
        statement
    )

    return [
        dict(row)
        for row
        in result.mappings().all()
    ]
