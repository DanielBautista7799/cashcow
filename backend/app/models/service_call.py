from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy import Enum as SqlEnum
from app.models.base import Base
from app.models.enums import ServiceCallPriority, ServiceCallStatus

if TYPE_CHECKING:
    from .atm import Atm
    from .diagnostic_report import DiagnosticReport
    from .technician import Technician

class ServiceCall(Base):
    __tablename__= "service_calls"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    priority: Mapped[ServiceCallPriority] = mapped_column(
        SqlEnum(
            ServiceCallPriority,
            name="service_call_priority",
            values_callable = lambda enums_cls:[members.value for members in enums_cls]
        )
    )
    status: Mapped[ServiceCallStatus] = mapped_column(
        SqlEnum(
            ServiceCallStatus,
            name = "service_call_status",
            values_callable = lambda enums_cls:[members.value for members in enums_cls]
        )
    )
    atm_id: Mapped[int] = mapped_column(Integer, ForeignKey("atms.id") )
    technician_id : Mapped[int]= mapped_column(Integer, ForeignKey("technicians.id"))
    atm: Mapped["Atm"] = relationship(back_populates="service_calls")
    diagnostic_reports: Mapped[list["DiagnosticReport"]] = relationship(back_populates="service_call")
    technician: Mapped["Technician"] = relationship(back_populates="service_calls")

    def mark_completed(self) -> None:
        self.status = ServiceCallStatus.COMPLETED

    def mark_failed(self) -> None:
        self.status = ServiceCallStatus.FAILED