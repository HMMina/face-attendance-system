"""
Face Template Model for Rolling Template System
Stores maximum 3 face templates per employee with automatic rotation
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ARRAY, CheckConstraint, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class FaceTemplate(Base):
    __tablename__ = "face_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(String(100), nullable=False, unique=True)  # Unique image filename
    
    # 512-dimensional face embedding vector from InsightFace
    embedding_vector = Column(ARRAY(Float), nullable=False)
    
    # Template slot (1, 2, or 3)
    template_order = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Source information
    created_from = Column(String(20), nullable=False)  # 'ADMIN_UPLOAD' or 'ATTENDANCE'
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)         # Image quality (0.0-1.0)
    # confidence_score = Column(Float, default=0.0)      # Recognition confidence when created - NOT IN DB
    
    # Performance tracking - THESE FIELDS ARE NOT IN DATABASE YET
    # match_count = Column(Integer, default=0)           # How many times this template was matched
    # last_matched = Column(DateTime, nullable=True)     # Last time this template was used for matching
    # avg_match_confidence = Column(Float, default=0.0)  # Average confidence when matching
    
    # Template constraints
    __table_args__ = (
        UniqueConstraint('employee_id', 'template_order', name='unique_employee_template'),
        CheckConstraint('template_order IN (1, 2, 3)', name='template_order_check'),
        CheckConstraint('created_from IN (\'ADMIN_UPLOAD\', \'ATTENDANCE\')', name='created_from_check'),
        CheckConstraint('quality_score >= 0.0 AND quality_score <= 1.0', name='quality_score_check'),
        CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='confidence_score_check'),
    )
    
    # Relationship with Employee
    employee = relationship("Employee", back_populates="face_templates")
    
    def __repr__(self):
        return f"<FaceTemplate(id={self.id}, employee_id={self.employee_id}, order={self.template_order})>"
    
    @property
    def age_days(self):
        """Calculate how many days old this template is"""
        return (datetime.datetime.utcnow() - self.created_at).days
    
    @property
    def embedding_size(self):
        """Get size of embedding vector"""
        return len(self.embedding_vector) if self.embedding_vector else 0
