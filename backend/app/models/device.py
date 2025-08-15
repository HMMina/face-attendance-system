"""
Device model for kiosk device management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import Base
import datetime

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    name = Column(String)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    token = Column(String)
    ip_address = Column(String)
    network_status = Column(String, default="offline")
