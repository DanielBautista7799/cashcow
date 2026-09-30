from __future__ import annotations


from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from .branch import Branch
    from .service_call import ServiceCall

class Technician(Base):
    __tablename__ = "technicians"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branches.id"))

    branch: Mapped["Branch"] = relationship(back_populates="technicians")
    service_calls: Mapped[list["ServiceCall"]] = relationship(back_populates="technician")