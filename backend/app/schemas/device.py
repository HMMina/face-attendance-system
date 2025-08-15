"""
Pydantic schemas for device management
"""
from pydantic import BaseModel
from typing import Optional
import datetime

class DeviceBase(BaseModel):
    device_id: str
    name: Optional[str] = None
    ip_address: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceOut(DeviceBase):
    id: int
    registered_at: datetime.datetime
    last_seen: datetime.datetime
    is_active: bool
    network_status: str

    model_config = {"from_attributes": True}

class DeviceHeartbeat(BaseModel):
    device_id: str
    timestamp: datetime.datetime
    network_status: str
