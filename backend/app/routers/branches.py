from fastapi import Depends, FastAPI, Query
from sqlalchemy import case, func, select

from app.schemas.branch import MaintenanceFlag, ReportingLineResult, TechnicianActiveServiceCalls
from app.dependencies import get_current_user, get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.atm import Atm
from app.models.branch import Branch
from app.models.enums import AtmStatus, ServiceCallStatus
from app.models.service_call import ServiceCall
from app.models.technician import Technician


router = FastAPI("/branches", tags=["branches"])

@router.get("/maintenance-flags", response_model=list[MaintenanceFlag])
async def maintenance_flags( current_user:User = get_current_user(), db: AsyncSession = get_db()):
    maintenance_count = func.sum(
    case(
        (Atm.status == AtmStatus.MAINTENANCE, 1),
        else_=0,
    )
)

    total_atms = func.count(Atm.id)

    maintenance_pct = (
        maintenance_count * 100.0 / total_atms
    )

    statement = (
        select(
            Branch.id.label("Branch_id"),
            Branch.name.label("Branch_name"),
            total_atms.label("total_equipment"),
            maintenance_count.label("maintenance_count"),
            maintenance_pct.label("maintenance_percentage"),
        )
        .join(
            Atm,
            Atm.facility_id == Branch.id,
        )
        .group_by(
            Branch.id,
            Branch.name,
        )
        .having(maintenance_pct > 30)
        .order_by(Branch.id)
    )

    result = await db.execute(statement)

    return [
        dict(row)
        for row in result.mappings().all()
    ]



@router.get("/reporting-lines", response_model=ReportingLineResult)
async def reporting_lines(
    supervisor_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    statement = (
        select(
            Technician.id.label("technician_id"),
            Technician.name.label("technician_name"),
            func.count(ServiceCall.id).label("active_service_call_count"),
        )
        .join(
            Branch,
            Branch.id == Technician.branch_id,
        )
        .join(
            ServiceCall,
            ServiceCall.technician_id == Technician.id,
        )
        .where(
            Branch.supervisor_id == supervisor_id,
            ServiceCall.status.in_(
                [
                    ServiceCallStatus.PENDING,
                    ServiceCallStatus.IN_PROGRESS,
                ]
            ),
        )
        .group_by(
            Technician.id,
            Technician.name,
        )
        .order_by(Technician.id)
    )

    result = await db.execute(statement)

    technicians = [
        TechnicianActiveServiceCalls(**row)
        for row in result.mappings().all()
    ]

    return ReportingLineResult(
        supervisor_id=supervisor_id,
        technician_count=len(technicians),
        technicians=technicians,
    )