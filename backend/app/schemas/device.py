"""
Pydantic schemas for device management
"""
from pydantic import BaseModel
from typing import Optional
import datetime

class DeviceBase(BaseModel):
    device_id: Optional[str] = None  # Auto-generated if not provided
    name: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: Optional[bool] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceOut(DeviceBase):
    id: int
    device_id: str  # Always present in output
    registered_at: datetime.datetime
    last_seen: datetime.datetime
    is_active: bool
    network_status: str

    model_config = {"from_attributes": True}

class DeviceHeartbeat(BaseModel):
    device_id: str
    timestamp: datetime.datetime
    network_status: str
