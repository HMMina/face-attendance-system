"""
Employee schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class EmployeeBase(BaseModel):
    employee_id: Optional[str] = None  # Auto-generated if not provided
    name: str
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeOut(EmployeeBase):
    id: int
    employee_id: str  # Always present in output
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
