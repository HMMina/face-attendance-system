"""
Face Template Model with Enhanced Embedding System
Stores up to 4 face templates per employee:
- image_id 0: Primary avatar (never replaced)
- image_id 1,2,3: Secondary templates (replaceable during updates)
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ARRAY, CheckConstraint, UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class FaceTemplate(Base):
    __tablename__ = "face_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Image information
    image_id = Column(Integer, nullable=False)  # 0=avatar, 1,2,3=secondary templates
    filename = Column(String(200), nullable=False)  # Original filename
    file_path = Column(String(500), nullable=False)  # Full path to image file
    
    # 512-dimensional face embedding vector from InsightFace
    embedding_vector = Column(ARRAY(Float), nullable=False)
    
    # Status and metadata
    is_primary = Column(Boolean, default=False)  # True if image_id = 0 (avatar)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Source information
    created_from = Column(String(20), nullable=False)  # 'ADMIN_UPLOAD' or 'ATTENDANCE'
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)         # Image quality (0.0-1.0)
    confidence_score = Column(Float, default=0.0)      # Embedding extraction confidence
    
    # Performance tracking
    match_count = Column(Integer, default=0)           # How many times this template was matched
    last_matched = Column(DateTime, nullable=True)     # Last time this template was used for matching
    avg_match_confidence = Column(Float, default=0.0)  # Average confidence when matching
    
    # Template constraints
    __table_args__ = (
        UniqueConstraint('employee_id', 'image_id', name='unique_employee_image_id'),
        CheckConstraint('image_id >= 0 AND image_id <= 3', name='image_id_check'),
        CheckConstraint('created_from IN (\'ADMIN_UPLOAD\', \'ATTENDANCE\')', name='created_from_check'),
        CheckConstraint('quality_score >= 0.0 AND quality_score <= 1.0', name='quality_score_check'),
        CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='confidence_score_check'),
    )
    
    # Relationship with Employee
    employee = relationship("Employee", back_populates="face_templates")
    
    def __repr__(self):
        return f"<FaceTemplate(id={self.id}, employee_id={self.employee_id}, image_id={self.image_id}, is_primary={self.is_primary})>"
    
    @property
    def age_days(self):
        """Calculate how many days old this template is"""
        return (datetime.datetime.utcnow() - self.created_at).days
    
    @property
    def embedding_size(self):
        """Get size of embedding vector"""
        return len(self.embedding_vector) if self.embedding_vector else 0
    
    @property
    def is_avatar(self):
        """Check if this is the primary avatar (image_id = 0)"""
        return self.image_id == 0
    
    @property
    def is_replaceable(self):
        """Check if this template can be replaced (image_id > 0)"""
        return self.image_id > 0
    
    def update_match_stats(self, confidence: float):
        """Update matching statistics when this template is used"""
        self.match_count += 1
        self.last_matched = datetime.datetime.utcnow()
        
        # Update average confidence
        if self.avg_match_confidence == 0.0:
            self.avg_match_confidence = confidence
        else:
            # Running average formula
            self.avg_match_confidence = (
                (self.avg_match_confidence * (self.match_count - 1) + confidence) / self.match_count
            )
