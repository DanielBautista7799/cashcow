from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AtmStatus


if TYPE_CHECKING:
    from .branch import Branch
    from .service_call import ServiceCall


class Atm(Base):
    __tablename__ = "atms"

    __table_args__ = (
        CheckConstraint(
            "cash_level between 0 and 100",
            name="cash_level_range",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    serial_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    model: Mapped[str] = mapped_column(
        String(100)
    )

    status: Mapped[AtmStatus] = mapped_column(
        SqlEnum(
            AtmStatus,
            name="atm_status",
            values_callable=lambda enum_cls: [
                member.value
                for member in enum_cls
            ],
        )
    )

    cash_level: Mapped[Decimal] = mapped_column(
        Numeric(5, 2)
    )

    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id"),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    branch: Mapped["Branch"] = relationship(
        back_populates="atms"
    )

    service_calls: Mapped[list["ServiceCall"]] = relationship(
        back_populates="atm"
    )

    LOW_CASH_THRESHOLD = 20

    def is_low_cash(
        self,
        threshold: int | None = None,
    ) -> bool:
        limit = (
            threshold
            if threshold is not None
            else Atm.LOW_CASH_THRESHOLD
        )

        return self.cash_level < limit

    def needs_maintenance(self) -> bool:
        return (
            self.status
            == AtmStatus.MAINTENANCE
        )
