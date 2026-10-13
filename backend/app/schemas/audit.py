from datetime import datetime

from pydantic import BaseModel


class AuditEntryRead(BaseModel):
    id: int
    record_type: str
    record_id: int
    action: str
    acting_user_id: int
    acting_username: str
    created_at: datetime
    changes: dict
