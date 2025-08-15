"""
Employee schemas
"""
from pydantic import BaseModel
from typing import Optional
import datetime

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    department: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
