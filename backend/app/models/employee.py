"""
Employee model
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    name = Column(String)
    department = Column(String)
    email = Column(String)
    phone = Column(String)
    position = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship với face templates
    face_templates = relationship("FaceTemplate", back_populates="employee", cascade="all, delete-orphan")
