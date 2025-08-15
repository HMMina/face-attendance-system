"""
Network log model
"""
from sqlalchemy import Column, Integer, String, DateTime
from app.models.base import Base
import datetime

class NetworkLog(Base):
    __tablename__ = "network_logs"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String)
    event = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String)
    status = Column(String)
