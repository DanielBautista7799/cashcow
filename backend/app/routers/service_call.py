from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.service_call import ColocationDiscrepancyRead, ReliabilitiyMetric, ServiceCallRead, ServiceCallStatusUpdate
from app.dependencies import get_current_user, get_db, require_role
from app.models.enums import ServiceCallPriority, ServiceCallStatus, UserRole
from app.models.user import User
from app.models.service_call import ServiceCall
from app.models.atm import Atm
from app.models.technician import Technician


router =APIRouter(prefix= "/service-call", tags=["service-call"])   

@router.get("/discrepancies", response_model=list[ColocationDiscrepancyRead])
async def get_colocation_dependancies(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), priority: ServiceCallPriority | None = Query(
    default= None,
    description="Only return discrepancies for work orders of this priority"
)):
    statement = (select(ServiceCall.id.label("service_call_id"),
                        ServiceCall.title,
                        Atm.branch_id.label("atm_branch_id"),
                        Technician.branch_id.label("technician_branch_id"),)
                        .join(Technician, Technician.id == ServiceCall.technician_id)
                        .join(Atm, Atm.id == ServiceCall.atm_id)
                        .where(Atm.branch_id != Technician.branch_id)
                        )
    if priority is not None:
        statement = statement.where(ServiceCall.priority == priority)
    statement = statement.order_by(ServiceCall.id)

    result = await db.execute(statement)
    return [dict(row) for row in result.mappings().all()]

@router.get("/reliability", response_model=[ReliabilitiyMetric])
async def reliability_metrics(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    statement = (
        select(
            Atm.model,
            func.count(ServiceCall.id).label("total_work_orders"),
            func.sum(
                case(
                    (ServiceCall.status == ServiceCallStatus.COMPLETED, 1),
                    else_=0,
                )
            ).label("completed_count"),
            func.sum(
                case(
                    (ServiceCall.status == ServiceCallStatus.FAILED, 1),
                    else_=0,
                )
            ).label("failed_count"),
        )
        .join(ServiceCall, ServiceCall.atm_id == Atm.id)
        .group_by(Atm.model)
        .order_by(Atm.model)
    )

    result = await db.execute(statement)

    return [dict(row) for row in result.mappings().all()]





@router.get(path="/{service_call_id}", response_model=ServiceCallRead)
async def get_work_order(service_call_id:int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user))-> ServiceCall:
        service_call = await db.get(ServiceCall, service_call_id)
        if service_call is None:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail = (f"service call of id {service_call_id} not found")
            )
        return service_call

@router.patch("/{service_call_id}/status", response_model=ServiceCallRead)
async def update_work_order_status(service_call_id: int, update: ServiceCallStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TECHNICIAN)),):
    statement = (select(ServiceCall).where(ServiceCall.id == service_call_id))
    result = await db.execute(statement)
    service_call =  result.scalars().first()
    if service_call is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Work_order not found"
        )
    if update.status == ServiceCallStatus.COMPLETED:
        service_call.mark_completed()
    elif update.status == ServiceCallStatus.PENDING or update.status == ServiceCallStatus.IN_PROGRESS:
        service_call.status = update.status
    elif update.status == ServiceCallStatus.FAILED:
        service_call.mark_failed()
    await db.commit()
    await db.refresh(service_call)
    return service_call


