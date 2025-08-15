"""
Network status schemas
"""
from pydantic import BaseModel
from typing import Optional
import datetime

class NetworkLogBase(BaseModel):
    device_id: str
    event: str
    ip_address: Optional[str] = None
    status: Optional[str] = None

class NetworkLogOut(NetworkLogBase):
    id: int
    timestamp: datetime.datetime
    
    model_config = {"from_attributes": True}
