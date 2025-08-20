# 🚀 Face Embedding Model Implementation

"""
Face Embedding Model for storing InsightFace embeddings
Optimized for performance and reliability in single database approach
Stores 512-dimensional face embeddings for employee recognition
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, ARRAY, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from app.models.base import Base
import datetime

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 512-dimensional face embedding vector from InsightFace
    embedding_vector = Column(ARRAY(Float), nullable=False)
    
    # Optional: Compressed embedding for storage optimization
    embedding_compressed = Column(LargeBinary, nullable=True)
    
    # Checksum for deduplication and integrity
    embedding_checksum = Column(String(64), nullable=True, index=True)
    
    # Path to face photo used for generating this embedding
    face_photo_path = Column(String, nullable=True)
    
    # Confidence threshold for this specific embedding
    confidence_threshold = Column(Float, default=0.7)
    
    # Quality score of the face photo (0.0-1.0)
    photo_quality = Column(Float, default=0.0)
    
    # Registration metadata
    registered_by = Column(String, default="system")  # Who registered this face
    registration_device = Column(String, nullable=True)  # Device used for registration
    registration_method = Column(String, default="upload")  # upload, camera, import
    
    # Performance tracking (NEW)
    match_count = Column(Integer, default=0)  # How many times this embedding was matched
    avg_match_confidence = Column(Float, default=0.0)  # Average confidence over time
    confidence_history = Column(JSON, nullable=True)  # Track confidence degradation
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_primary = Column(Boolean, default=False, index=True)  # Primary embedding for employee
    needs_update = Column(Boolean, default=False)  # Flag for template aging
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_used = Column(DateTime, nullable=True, index=True)  # Last time this embedding was matched
    last_successful_match = Column(DateTime, nullable=True)  # Last high-confidence match
    
    # Embedding metadata (NEW)
    extraction_model = Column(String, default="InsightFace_Buffalo_L")  # Model used for extraction
    extraction_confidence = Column(Float, nullable=True)  # AI model confidence during extraction
    face_bbox = Column(JSON, nullable=True)  # Bounding box info {"x1": 100, "y1": 120, "x2": 200, "y2": 220}
    
    # Relationships
    employee = relationship("Employee", back_populates="face_embeddings")
    
    def __repr__(self):
        return f"<FaceEmbedding(id={self.id}, employee_id={self.employee_id}, active={self.is_active})>"

# Add to Employee model (update employee.py)
"""
Add this to Employee class:
    face_embeddings = relationship("FaceEmbedding", back_populates="employee")
"""
