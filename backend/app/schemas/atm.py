from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.enums import AtmStatus


class AtmBase(BaseModel):
    serial_number: str = Field(
        min_length=1,
        max_length=100,
    )

    model: str = Field(
        min_length=1,
        max_length=100,
    )

    status: AtmStatus = (
        AtmStatus.OPERATIONAL
    )

    cash_level: Decimal = Field(
        ge=0,
        le=100,
    )

    branch_id: int


class AtmCreate(AtmBase):
    pass


class AtmUpdate(BaseModel):
    serial_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    status: AtmStatus | None = None

    cash_level: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    branch_id: int | None = Field(
        default=None,
        ge=1,
    )


class AtmRead(AtmBase):
    id: int

    is_active: bool = True
    deleted_at: datetime | None = None
    deleted_by: int | None = None

    model_config = ConfigDict(
        from_attributes=True
    )
