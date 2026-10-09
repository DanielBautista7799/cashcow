from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AtmStatus

class AtmBase(BaseModel):
    serial_number: str = Field(min_length=1,max_length=100)
    model: str= Field(min_length=1,max_length=100)
    status: AtmStatus = AtmStatus.OPERATIONAL
    cash_level: Decimal = Field(ge=0, le=100 )
    branch_id: int

class AtmCreate(AtmBase):
    pass

class AtmRead(AtmBase):
    id: int
    model_config = ConfigDict(from_attributes=True)