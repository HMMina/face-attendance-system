"""
Employee model
"""
from sqlalchemy import Column, Integer, String, DateTime
from app.models.base import Base
import datetime

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    name = Column(String)
    department = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
