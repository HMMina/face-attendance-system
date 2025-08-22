"""
Face Template Service - 4-Slot System Management
Manages avatar (slot 0) and dynamic templates (slots 1-3)
"""
from sqlalchemy.orm import Session
from app.models.face_template import FaceTemplate
from app.models.employee import Employee
import logging
import datetime

logger = logging.getLogger(__name__)

class FaceTemplateService:
    """Service for managing 4-slot face template system"""
    
    @staticmethod
    def get_employee_templates(db: Session, employee_id: str):
        """Get all templates for an employee, ordered by slot"""
        return db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id
        ).order_by(FaceTemplate.template_order).all()
    
    @staticmethod
    def get_avatar_template(db: Session, employee_id: str):
        """Get avatar template (slot 0)"""
        return db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id,
            FaceTemplate.template_order == 0
        ).first()
    
    @staticmethod
    def get_dynamic_templates(db: Session, employee_id: str):
        """Get dynamic templates (slots 1-3)"""
        return db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id,
            FaceTemplate.template_order.in_([1, 2, 3])
        ).order_by(FaceTemplate.template_order).all()
    
    @staticmethod
    def set_avatar(db: Session, employee_id: str, embedding_vector, image_id: str, quality_score: float = 0.0):
        """Set or update avatar (slot 0) - Only from admin"""
        try:
            # Remove existing avatar
            existing_avatar = FaceTemplateService.get_avatar_template(db, employee_id)
            if existing_avatar:
                db.delete(existing_avatar)
            
            # Create new avatar
            avatar = FaceTemplate(
                employee_id=employee_id,
                image_id=image_id,
                embedding_vector=embedding_vector,
                template_order=0,
                created_from='ADMIN_UPLOAD',
                is_avatar=True,
                is_permanent=True,
                quality_score=quality_score
            )
            
            db.add(avatar)
            db.commit()
            db.refresh(avatar)
            
            # Update employee avatar path
            employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if employee:
                employee.avatar_photo_path = f"/api/v1/employees/{employee_id}/photo/0"
                db.commit()
            
            logger.info(f"Set avatar for employee {employee_id}")
            return avatar
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting avatar for {employee_id}: {e}")
            raise
    
    @staticmethod
    def add_dynamic_template(db: Session, employee_id: str, embedding_vector, image_id: str, 
                           created_from: str = 'KIOSK_ATTENDANCE', quality_score: float = 0.0):
        """Add new dynamic template, implementing rolling replacement"""
        try:
            # Get existing dynamic templates
            dynamic_templates = FaceTemplateService.get_dynamic_templates(db, employee_id)
            
            if len(dynamic_templates) < 3:
                # Find next available slot
                used_slots = [t.template_order for t in dynamic_templates]
                next_slot = next(i for i in [1, 2, 3] if i not in used_slots)
                
                new_template = FaceTemplate(
                    employee_id=employee_id,
                    image_id=image_id,
                    embedding_vector=embedding_vector,
                    template_order=next_slot,
                    created_from=created_from,
                    is_avatar=False,
                    is_permanent=False,
                    quality_score=quality_score
                )
                
            else:
                # Rolling replacement - replace oldest or lowest quality
                template_to_replace = min(dynamic_templates, 
                                        key=lambda t: (t.quality_score, -t.age_days))
                
                # Update existing template
                template_to_replace.image_id = image_id
                template_to_replace.embedding_vector = embedding_vector
                template_to_replace.created_from = created_from
                template_to_replace.quality_score = quality_score
                template_to_replace.created_at = datetime.datetime.utcnow()
                template_to_replace.match_count = 0
                template_to_replace.avg_match_confidence = 0.0
                
                new_template = template_to_replace
            
            db.add(new_template)
            db.commit()
            db.refresh(new_template)
            
            logger.info(f"Added dynamic template slot {new_template.template_order} for {employee_id}")
            return new_template
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding dynamic template for {employee_id}: {e}")
            raise
    
    @staticmethod
    def get_recognition_templates(db: Session, employee_id: str):
        """Get all templates for AI recognition (slots 0-3)"""
        return db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id
        ).order_by(FaceTemplate.template_order).all()
    
    @staticmethod
    def update_match_stats(db: Session, template_id: int, confidence: float):
        """Update template match statistics"""
        try:
            template = db.query(FaceTemplate).filter(FaceTemplate.id == template_id).first()
            if template:
                # Update match statistics
                old_avg = template.avg_match_confidence or 0.0
                old_count = template.match_count or 0
                
                new_count = old_count + 1
                new_avg = (old_avg * old_count + confidence) / new_count
                
                template.match_count = new_count
                template.avg_match_confidence = new_avg
                template.last_matched = datetime.datetime.utcnow()
                
                db.commit()
                logger.debug(f"Updated match stats for template {template_id}")
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating match stats for template {template_id}: {e}")
    
    @staticmethod
    def get_template_by_slot(db: Session, employee_id: str, slot: int):
        """Get template by specific slot number (0-3)"""
        return db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id,
            FaceTemplate.template_order == slot
        ).first()
