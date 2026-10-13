from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import (
    case,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_db,
    require_permission,
)
from app.models.atm import Atm
from app.models.audit_entry import AuditEntry
from app.models.enums import (
    ServiceCallPriority,
    ServiceCallStatus,
)
from app.models.service_call import ServiceCall
from app.models.technician import Technician
from app.models.user import User
from app.pagination import PageParams
from app.permissions import (
    Permission,
    permissions_for_role,
)
from app.schemas.audit import AuditEntryRead
from app.schemas.page import Page
from app.schemas.service_call import (
    ColocationDiscrepancyRead,
    ReliabilityMetric,
    ServiceCallCreate,
    ServiceCallRead,
    ServiceCallStatusUpdate,
    ServiceCallUpdate,
)
from app.services.operations import (
    create_service_call as create_service_call_record,
    restore_service_call,
    soft_delete_service_call,
    update_service_call,
    update_service_call_status as update_status_record,
)


router = APIRouter(
    prefix="/service-call",
    tags=["service-call"],
)


SORT_COLUMNS = {
    "id": ServiceCall.id,
    "title": ServiceCall.title,
    "priority": ServiceCall.priority,
    "status": ServiceCall.status,
    "atm_id": ServiceCall.atm_id,
    "technician_id": (
        ServiceCall.technician_id
    ),
}


@router.get(
    "",
    response_model=Page[ServiceCallRead],
)
async def list_service_calls(
    pagination: PageParams = Depends(),
    status_filter: ServiceCallStatus | None = Query(
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
            Permission.JOB_READ
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
        ServiceCall.is_active.is_(True)
    ]

    if status_filter is not None:
        conditions.append(
            ServiceCall.status
            == status_filter
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
                ServiceCall.title.ilike(
                    search_value
                ),
            )
        )

    count_statement = (
        select(
            func.count(
                ServiceCall.id
            )
        )
        .select_from(ServiceCall)
        .join(
            Atm,
            Atm.id
            == ServiceCall.atm_id,
        )
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
        select(ServiceCall)
        .join(
            Atm,
            Atm.id
            == ServiceCall.atm_id,
        )
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
    response_model=list[ServiceCallRead],
)
async def list_inactive_service_calls(
    _: User = Depends(
        require_permission(
            Permission.JOB_WRITE
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ServiceCall)
        .where(
            ServiceCall.is_active.is_(
                False
            )
        )
        .order_by(ServiceCall.id)
    )

    return list(
        result.scalars().all()
    )


@router.get(
    "/discrepancies",
    response_model=list[
        ColocationDiscrepancyRead
    ],
)
async def get_colocation_discrepancies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.ANALYTICS_READ
        )
    ),
    priority: (
        ServiceCallPriority | None
    ) = Query(default=None),
):
    statement = (
        select(
            ServiceCall.id.label(
                "service_call_id"
            ),
            ServiceCall.title,
            Atm.branch_id.label(
                "atm_branch_id"
            ),
            Technician.branch_id.label(
                "technician_branch_id"
            ),
        )
        .join(
            Technician,
            Technician.id
            == ServiceCall.technician_id,
        )
        .join(
            Atm,
            Atm.id
            == ServiceCall.atm_id,
        )
        .where(
            ServiceCall.is_active.is_(
                True
            ),
            Atm.is_active.is_(True),
            Atm.branch_id
            != Technician.branch_id,
        )
    )

    if priority is not None:
        statement = statement.where(
            ServiceCall.priority
            == priority
        )

    statement = statement.order_by(
        ServiceCall.id
    )

    result = await db.execute(
        statement
    )

    return [
        dict(row)
        for row
        in result.mappings().all()
    ]


@router.get(
    "/reliability",
    response_model=list[
        ReliabilityMetric
    ],
)
async def reliability_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.ANALYTICS_READ
        )
    ),
):
    statement = (
        select(
            Atm.model,
            func.count(
                ServiceCall.id
            ).label(
                "total_service_calls"
            ),
            func.sum(
                case(
                    (
                        ServiceCall.status
                        == ServiceCallStatus.COMPLETED,
                        1,
                    ),
                    else_=0,
                )
            ).label(
                "service_calls_completed"
            ),
            func.sum(
                case(
                    (
                        ServiceCall.status
                        == ServiceCallStatus.FAILED,
                        1,
                    ),
                    else_=0,
                )
            ).label(
                "service_calls_failed"
            ),
        )
        .join(
            ServiceCall,
            ServiceCall.atm_id
            == Atm.id,
        )
        .where(
            Atm.is_active.is_(True),
            ServiceCall.is_active.is_(
                True
            ),
        )
        .group_by(Atm.model)
        .order_by(Atm.model)
    )

    result = await db.execute(
        statement
    )

    return [
        dict(row)
        for row
        in result.mappings().all()
    ]


@router.post(
    "",
    response_model=ServiceCallRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_service_call(
    payload: ServiceCallCreate,
    current_user: User = Depends(
        require_permission(
            Permission.JOB_WRITE
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    atm_result = await db.execute(
        select(Atm).where(
            Atm.id == payload.atm_id,
            Atm.is_active.is_(True),
        )
    )

    if (
        atm_result.scalar_one_or_none()
        is None
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "Active ATM not found"
            ),
        )

    technician = await db.get(
        Technician,
        payload.technician_id,
    )

    if technician is None:
        raise HTTPException(
            status_code=404,
            detail="Technician not found",
        )

    return await create_service_call_record(
        db,
        payload.model_dump(),
        current_user,
    )


@router.get(
    "/{service_call_id}",
    response_model=ServiceCallRead,
)
async def get_service_call(
    service_call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.JOB_READ
        )
    ),
):
    result = await db.execute(
        select(ServiceCall).where(
            ServiceCall.id
            == service_call_id,
            ServiceCall.is_active.is_(
                True
            ),
        )
    )

    service_call = (
        result.scalar_one_or_none()
    )

    if service_call is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Service call not found"
            ),
        )

    return service_call


@router.patch(
    "/{service_call_id}",
    response_model=ServiceCallRead,
)
async def patch_service_call(
    service_call_id: int,
    payload: ServiceCallUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.JOB_WRITE
        )
    ),
):
    result = await db.execute(
        select(ServiceCall).where(
            ServiceCall.id
            == service_call_id,
            ServiceCall.is_active.is_(
                True
            ),
        )
    )

    service_call = (
        result.scalar_one_or_none()
    )

    if service_call is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Service call not found"
            ),
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
                "Service call update "
                "fields cannot be null"
            ),
        )

    if "atm_id" in values:
        atm_result = await db.execute(
            select(Atm).where(
                Atm.id
                == values["atm_id"],
                Atm.is_active.is_(
                    True
                ),
            )
        )

        if (
            atm_result.scalar_one_or_none()
            is None
        ):
            raise HTTPException(
                status_code=404,
                detail=(
                    "Active ATM not found"
                ),
            )

    if "technician_id" in values:
        technician = await db.get(
            Technician,
            values["technician_id"],
        )

        if technician is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Technician not found"
                ),
            )

    return await update_service_call(
        db,
        service_call,
        values,
        current_user,
    )


@router.patch(
    "/{service_call_id}/status",
    response_model=ServiceCallRead,
)
async def update_service_call_status(
    service_call_id: int,
    update: ServiceCallStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.JOB_STATUS_WRITE
        )
    ),
):
    result = await db.execute(
        select(ServiceCall).where(
            ServiceCall.id
            == service_call_id,
            ServiceCall.is_active.is_(
                True
            ),
        )
    )

    service_call = (
        result.scalar_one_or_none()
    )

    if service_call is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Service call not found"
            ),
        )

    return await update_status_record(
        db,
        service_call,
        update.status,
        current_user,
    )


@router.delete(
    "/{service_call_id}",
    response_model=ServiceCallRead,
)
async def delete_service_call(
    service_call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.JOB_WRITE
        )
    ),
):
    result = await db.execute(
        select(ServiceCall).where(
            ServiceCall.id
            == service_call_id,
            ServiceCall.is_active.is_(
                True
            ),
        )
    )

    service_call = (
        result.scalar_one_or_none()
    )

    if service_call is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Service call not found"
            ),
        )

    return (
        await soft_delete_service_call(
            db,
            service_call,
            current_user,
        )
    )


@router.post(
    "/{service_call_id}/restore",
    response_model=ServiceCallRead,
)
async def restore_deleted_service_call(
    service_call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.JOB_WRITE
        )
    ),
):
    result = await db.execute(
        select(ServiceCall).where(
            ServiceCall.id
            == service_call_id,
            ServiceCall.is_active.is_(
                False
            ),
        )
    )

    service_call = (
        result.scalar_one_or_none()
    )

    if service_call is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Inactive service call "
                "not found"
            ),
        )

    return await restore_service_call(
        db,
        service_call,
        current_user,
    )


@router.get(
    "/{service_call_id}/history",
    response_model=list[AuditEntryRead],
)
async def get_service_call_history(
    service_call_id: int,
    current_user: User = Depends(
        require_permission(
            Permission.AUDIT_READ
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    service_call = await db.get(
        ServiceCall,
        service_call_id,
    )

    if service_call is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Service call not found"
            ),
        )

    permissions = permissions_for_role(
        current_user.role
    )

    if (
        not service_call.is_active
        and Permission.JOB_WRITE
        not in permissions
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "Service call not found"
            ),
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
            == "service_call",
            AuditEntry.record_id
            == service_call_id,
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
