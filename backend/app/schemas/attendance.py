"""
Attendance schemas
"""
from pydantic import BaseModel
from typing import Optional, Literal
import datetime

class AttendanceBase(BaseModel):
    employee_id: str
    device_id: str
    confidence: float
    image_path: Optional[str] = None
    action_type: Literal["CHECK_IN", "CHECK_OUT"] = "CHECK_IN"

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceOut(AttendanceBase):
    id: int
    timestamp: datetime.datetime
    
    model_config = {"from_attributes": True}
