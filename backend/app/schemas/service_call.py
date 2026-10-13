from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.enums import (
    ServiceCallPriority,
    ServiceCallStatus,
)


class ServiceCallCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
    )

    priority: ServiceCallPriority

    status: ServiceCallStatus = (
        ServiceCallStatus.PENDING
    )

    atm_id: int = Field(ge=1)
    technician_id: int = Field(ge=1)


class ServiceCallUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    priority: (
        ServiceCallPriority | None
    ) = None

    atm_id: int | None = Field(
        default=None,
        ge=1,
    )

    technician_id: int | None = Field(
        default=None,
        ge=1,
    )


class ServiceCallRead(BaseModel):
    id: int

    title: str = Field(
        min_length=1,
        max_length=100,
    )

    priority: ServiceCallPriority
    status: ServiceCallStatus

    atm_id: int
    technician_id: int

    is_active: bool = True
    deleted_at: datetime | None = None
    deleted_by: int | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class ServiceCallStatusUpdate(BaseModel):
    status: ServiceCallStatus


class ColocationDiscrepancyRead(BaseModel):
    service_call_id: int

    title: str = Field(
        min_length=1,
        max_length=100,
    )

    atm_branch_id: int
    technician_branch_id: int


class ReliabilityMetric(BaseModel):
    model: str
    total_service_calls: int
    service_calls_completed: int
    service_calls_failed: int
