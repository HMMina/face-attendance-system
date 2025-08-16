"""
Attendance model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from app.models.base import Base
import datetime

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"))
    device_id = Column(String, ForeignKey("devices.device_id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    confidence = Column(Float)
    image_path = Column(String)
    action_type = Column(String, default="CHECK_IN", nullable=False)
