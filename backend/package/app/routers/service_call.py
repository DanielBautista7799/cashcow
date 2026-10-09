from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models.atm import Atm
from app.models.enums import ServiceCallPriority, ServiceCallStatus, UserRole
from app.models.service_call import ServiceCall
from app.models.technician import Technician
from app.models.user import User
from app.pagination import PageParams
from app.schemas.page import Page
from app.schemas.service_call import (
    ColocationDiscrepancyRead,
    ReliabilityMetric,
    ServiceCallRead,
    ServiceCallStatusUpdate,
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
    "technician_id": ServiceCall.technician_id,
}


@router.get("", response_model=Page[ServiceCallRead])
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if pagination.sort_by not in SORT_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid sort field",
        )

    conditions = []

    if status_filter is not None:
        conditions.append(
            ServiceCall.status == status_filter
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
                ServiceCall.title.ilike(search_value),
            )
        )

    count_statement = (
        select(func.count(ServiceCall.id))
        .select_from(ServiceCall)
        .join(Atm, Atm.id == ServiceCall.atm_id)
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
        select(ServiceCall)
        .join(Atm, Atm.id == ServiceCall.atm_id)
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


@router.get(
    "/discrepancies",
    response_model=list[ColocationDiscrepancyRead],
)
async def get_colocation_discrepancies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    priority: ServiceCallPriority | None = Query(
        default=None
    ),
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
            Atm.id == ServiceCall.atm_id,
        )
        .where(
            Atm.branch_id
            != Technician.branch_id
        )
    )

    if priority is not None:
        statement = statement.where(
            ServiceCall.priority == priority
        )

    statement = statement.order_by(
        ServiceCall.id
    )

    result = await db.execute(statement)

    return [
        dict(row)
        for row
        in result.mappings().all()
    ]


@router.get(
    "/reliability",
    response_model=list[ReliabilityMetric],
)
async def reliability_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(
            Atm.model,
            func.count(
                ServiceCall.id
            ).label("total_service_calls"),
            func.sum(
                case(
                    (
                        ServiceCall.status
                        == ServiceCallStatus.COMPLETED,
                        1,
                    ),
                    else_=0,
                )
            ).label("service_calls_completed"),
            func.sum(
                case(
                    (
                        ServiceCall.status
                        == ServiceCallStatus.FAILED,
                        1,
                    ),
                    else_=0,
                )
            ).label("service_calls_failed"),
        )
        .join(
            ServiceCall,
            ServiceCall.atm_id == Atm.id,
        )
        .group_by(Atm.model)
        .order_by(Atm.model)
    )

    result = await db.execute(statement)

    return [
        dict(row)
        for row
        in result.mappings().all()
    ]


@router.get(
    "/{service_call_id}",
    response_model=ServiceCallRead,
)
async def get_service_call(
    service_call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service_call = await db.get(
        ServiceCall,
        service_call_id,
    )

    if service_call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service call not found",
        )

    return service_call


@router.patch(
    "/{service_call_id}/status",
    response_model=ServiceCallRead,
)
async def update_service_call_status(
    service_call_id: int,
    update: ServiceCallStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.TECHNICIAN,
        )
    ),
):
    result = await db.execute(
        select(ServiceCall).where(
            ServiceCall.id == service_call_id
        )
    )

    service_call = result.scalars().first()

    if service_call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service call not found",
        )

    if update.status == ServiceCallStatus.COMPLETED:
        service_call.mark_completed()

    elif update.status == ServiceCallStatus.FAILED:
        service_call.mark_failed()

    else:
        service_call.status = update.status

    await db.commit()
    await db.refresh(service_call)

    return service_call
