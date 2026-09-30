from pydantic import BaseModel

class MaintenanceFlag(BaseModel):
    branch_id:int
    branch_name:str
    total_atms: int
    maintenance_count: int
    maintenance_percentage: float

class TechnicianActiveServiceCalls(BaseModel):
    technician_id: int
    technician_name: str
    active_service_call_count: int

class ReportingLineResult(BaseModel):
    supervisor_id:int
    technician_count: int
    technician: list[TechnicianActiveServiceCalls]