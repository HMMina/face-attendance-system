"""
Template Manager Service for Rolling Template System
Manages face templates with automatic rotation and quality control
ALL DATA STORED IN POSTGRESQL DATABASE - NO FILE SYSTEM STORAGE
"""
import numpy as np
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.face_template import FaceTemplate
from app.models.employee import Employee
import logging

logger = logging.getLogger(__name__)

class TemplateManagerService:
    """
    Service for managing rolling face templates - DATABASE ONLY
    - Maximum 3 templates per employee
    - Automatic rotation every 10 days
    - Quality and confidence thresholds
    - ALL embeddings stored in PostgreSQL database
    """
    
    # Configuration constants
    MAX_TEMPLATES_PER_EMPLOYEE = 3
    TEMPLATE_REPLACEMENT_DAYS = 10
    MIN_CONFIDENCE_FOR_TEMPLATE = 0.85
    MIN_QUALITY_SCORE = 0.8
        
    def _generate_filename(self, employee_id: str, image_id: int) -> str:
        """Generate filename for image storage"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{employee_id}_image_{image_id}_{timestamp}.jpg"
    
    async def add_admin_template(self, db: Session, employee_id: str, 
                               image: np.ndarray, quality_score: float, 
                               confidence_score: float) -> Dict:
        """
        Add template from admin upload (always slot 1)
        """
        try:
            # Validate employee exists
            employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if not employee:
                return {"success": False, "message": f"Employee {employee_id} not found"}
            
            # Quality check
            if quality_score < self.MIN_QUALITY_SCORE:
                return {"success": False, "message": f"Image quality too low: {quality_score}"}
            
            # Check if template slot 1 already exists (admin upload)
            existing_admin_template = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id,
                FaceTemplate.template_order == 1,
                FaceTemplate.created_from == 'ADMIN_UPLOAD'
            ).first()
            
            if existing_admin_template:
                # Remove existing admin template from database
                db.delete(existing_admin_template)
            
            # Generate unique image ID for database record
            image_id = self._generate_image_id(employee_id, 1)
            
            # Extract embedding directly - NO FILE STORAGE
            from app.services.real_ai_service import get_ai_service
            ai_service = get_ai_service()
            embedding = ai_service.extract_embedding(image)
            
            if embedding is None:
                return {"success": False, "message": "Failed to extract face embedding"}
            
            # Create template record - EMBEDDING STORED IN DATABASE
            template = FaceTemplate(
                employee_id=employee_id,
                image_id=image_id,
                embedding_vector=embedding.tolist(),
                template_order=1,
                created_from='ADMIN_UPLOAD',
                quality_score=quality_score,
                confidence_score=confidence_score
            )
            
            db.add(template)
            db.commit()
            db.refresh(template)
            
            logger.info(f"Added admin template for employee {employee_id} (DATABASE ONLY)")
            
            return {
                "success": True,
                "template_id": template.id,
                "image_id": image_id,
                "template_order": 1,
                "embedding_dimensions": len(embedding),
                "storage_location": "PostgreSQL Database",
                "message": "Admin template stored in database successfully"
            }
            
        except Exception as e:
            logger.error(f"Error adding admin template: {e}")
            db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def add_attendance_template(self, db: Session, employee_id: str,
                                    image: np.ndarray, quality_score: float,
                                    confidence_score: float) -> Dict:
        """
        Add template from attendance recognition
        """
        try:
            # Check if we should add this template
            should_add, reason = await self._should_add_template(
                db, employee_id, confidence_score, quality_score
            )
            
            if not should_add:
                return {"success": False, "message": reason}
            
            # Find available template slot
            template_order = await self._find_template_slot(db, employee_id)
            
            # If replacing existing template, remove from database
            existing_template = db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id,
                FaceTemplate.template_order == template_order
            ).first()
            
            if existing_template:
                db.delete(existing_template)
            
            # Generate new image ID for database record
            image_id = self._generate_image_id(employee_id, template_order)
            
            # Extract embedding directly - NO FILE STORAGE
            from app.services.real_ai_service import get_ai_service
            ai_service = get_ai_service()
            embedding = ai_service.extract_embedding(image)
            
            if embedding is None:
                return {"success": False, "message": "Failed to extract face embedding"}
            
            # Create template record - EMBEDDING STORED IN DATABASE  
            template = FaceTemplate(
                employee_id=employee_id,
                image_id=image_id,
                embedding_vector=embedding.tolist(),
                template_order=template_order,
                created_from='ATTENDANCE',
                quality_score=quality_score,
                confidence_score=confidence_score
            )
            
            db.add(template)
            db.commit()
            db.refresh(template)
            
            logger.info(f"Added attendance template {template_order} for employee {employee_id} (DATABASE ONLY)")
            
            return {
                "success": True,
                "template_id": template.id,
                "image_id": image_id,
                "template_order": template_order,
                "embedding_dimensions": len(embedding),
                "storage_location": "PostgreSQL Database",
                "message": f"Attendance template {template_order} stored in database successfully"
            }
            
        except Exception as e:
            logger.error(f"Error adding attendance template: {e}")
            db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def _should_add_template(self, db: Session, employee_id: str,
                                 confidence: float, quality: float) -> Tuple[bool, str]:
        """Check if we should add a new template"""
        
        # Quality and confidence checks
        if confidence < self.MIN_CONFIDENCE_FOR_TEMPLATE:
            return False, f"Confidence too low: {confidence}"
        
        if quality < self.MIN_QUALITY_SCORE:
            return False, f"Quality too low: {quality}"
        
        # Get current templates
        current_templates = db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id
        ).all()
        
        current_count = len(current_templates)
        
        # If less than max, always add
        if current_count < self.MAX_TEMPLATES_PER_EMPLOYEE:
            return True, "Available slot found"
        
        # If at max, check if oldest template is old enough to replace
        oldest_template = min(current_templates, key=lambda t: t.created_at)
        days_old = (datetime.utcnow() - oldest_template.created_at).days
        
        if days_old >= self.TEMPLATE_REPLACEMENT_DAYS:
            return True, f"Replacing template {oldest_template.template_order} (age: {days_old} days)"
        
        return False, f"No replacement needed. Oldest template age: {days_old} days"
    
    async def _find_template_slot(self, db: Session, employee_id: str) -> int:
        """Find available template slot or slot to replace"""
        
        existing_templates = db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id
        ).all()
        
        # If less than max, find next available slot
        if len(existing_templates) < self.MAX_TEMPLATES_PER_EMPLOYEE:
            used_orders = [t.template_order for t in existing_templates]
            for order in [1, 2, 3]:
                if order not in used_orders:
                    return order
        
        # If at max, find oldest template to replace
        oldest_template = min(existing_templates, key=lambda t: t.created_at)
        return oldest_template.template_order
    
    async def get_employee_templates(self, db: Session, employee_id: str) -> List[FaceTemplate]:
        """Get all templates for an employee from database"""
        return db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id
        ).order_by(FaceTemplate.template_order).all()
    
    async def get_all_active_templates(self, db: Session) -> List[FaceTemplate]:
        """Get all active templates for recognition"""
        return db.query(FaceTemplate).all()
    
    async def update_template_performance(self, db: Session, template_id: int, 
                                        match_confidence: float):
        """Update template performance metrics"""
        try:
            template = db.query(FaceTemplate).filter(FaceTemplate.id == template_id).first()
            
            if template:
                # Update running average
                total_matches = template.match_count
                current_avg = template.avg_match_confidence or 0
                
                new_avg = (current_avg * total_matches + match_confidence) / (total_matches + 1)
                
                template.avg_match_confidence = new_avg
                template.match_count += 1
                template.last_matched = datetime.utcnow()
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Error updating template performance: {e}")
            db.rollback()
    
    async def get_template_stats(self, db: Session) -> Dict:
        """Get template system statistics from database"""
        try:
            total_templates = db.query(FaceTemplate).count()
            admin_templates = db.query(FaceTemplate).filter(
                FaceTemplate.created_from == 'ADMIN_UPLOAD'
            ).count()
            attendance_templates = db.query(FaceTemplate).filter(
                FaceTemplate.created_from == 'ATTENDANCE'
            ).count()
            
            # Get employees with different template counts
            from sqlalchemy import text
            
            employees_with_1_template = db.execute(text("""
                SELECT COUNT(DISTINCT employee_id) 
                FROM face_templates 
                GROUP BY employee_id 
                HAVING COUNT(*) = 1
            """)).scalar() or 0
            
            employees_with_2_templates = db.execute(text("""
                SELECT COUNT(DISTINCT employee_id) 
                FROM face_templates 
                GROUP BY employee_id 
                HAVING COUNT(*) = 2
            """)).scalar() or 0
            
            employees_with_3_templates = db.execute(text("""
                SELECT COUNT(DISTINCT employee_id) 
                FROM face_templates 
                GROUP BY employee_id 
                HAVING COUNT(*) = 3
            """)).scalar() or 0
            
            return {
                "total_templates": total_templates,
                "admin_templates": admin_templates,
                "attendance_templates": attendance_templates,
                "employees_with_1_template": employees_with_1_template,
                "employees_with_2_templates": employees_with_2_templates,
                "employees_with_3_templates": employees_with_3_templates,
                "storage_location": "PostgreSQL Database",
                "embedding_dimensions": 512,
                "system_type": "Database-Only Rolling Template System"
            }
            
        except Exception as e:
            logger.error(f"Error getting template stats: {e}")
            return {}
