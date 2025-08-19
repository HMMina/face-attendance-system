# 🚀 Face Embedding Model Implementation

"""
Face Embedding Model for storing InsightFace embeddings
Stores 512-dimensional face embeddings for employee recognition
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    
    # 512-dimensional face embedding vector from InsightFace
    embedding_vector = Column(ARRAY(Float), nullable=False)
    
    # Path to face photo used for generating this embedding
    face_photo_path = Column(String, nullable=True)
    
    # Confidence threshold for this specific embedding
    confidence_threshold = Column(Float, default=0.7)
    
    # Quality score of the face photo (0.0-1.0)
    photo_quality = Column(Float, default=0.0)
    
    # Registration metadata
    registered_by = Column(String, default="system")  # Who registered this face
    registration_device = Column(String, nullable=True)  # Device used for registration
    
    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary embedding for employee
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_used = Column(DateTime, nullable=True)  # Last time this embedding was matched
    
    # Relationships
    employee = relationship("Employee", back_populates="face_embeddings")

# Add to Employee model (update employee.py)
"""
Add this to Employee class:
    face_embeddings = relationship("FaceEmbedding", back_populates="employee")
"""
