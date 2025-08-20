"""
API endpoints for Template Management System
Provides RESTful interface for rolling template operations
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import cv2
import numpy as np
from app.config.database import get_db
from app.services.template_manager_service import TemplateManagerService
from app.services.enhanced_recognition_service import get_enhanced_recognition_service
from app.models.employee import Employee
from app.models.face_template import FaceTemplate
import io
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/templates", tags=["Template Management"])

# Service instances
template_manager = TemplateManagerService()
recognition_service = get_enhanced_recognition_service()

def decode_image(image_file: UploadFile) -> np.ndarray:
    """Decode uploaded image file to numpy array"""
    try:
        # Read image bytes
        image_bytes = image_file.file.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")
        
        return image
    
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

@router.post("/admin/upload")
async def upload_admin_template(
    employee_id: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload admin template for employee (slot 1)
    This replaces any existing admin template
    """
    try:
        # Validate employee exists
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
        
        # Decode image
        image_array = decode_image(image)
        
        # Extract face and calculate quality
        from app.services.real_ai_service import get_ai_service
        ai_service = get_ai_service()
        
        # Detect face
        detections = ai_service.detect_faces(image_array)
        if not detections:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        # Use best detection
        best_detection = max(detections, key=lambda x: x.get('confidence', 0))
        bbox = best_detection.get('bbox')
        
        # Calculate quality scores
        quality_score = ai_service._calculate_image_quality(image_array)
        confidence_score = best_detection.get('confidence', 0.8)
        
        # Add admin template
        result = await template_manager.add_admin_template(
            db, employee_id, image_array, quality_score, confidence_score
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "success": True,
            "message": "Admin template uploaded successfully",
            "template_id": result["template_id"],
            "image_id": result["image_id"],
            "quality_score": quality_score,
            "confidence_score": confidence_score,
            "employee": {
                "employee_id": employee.employee_id,
                "full_name": employee.full_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading admin template: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/employee/{employee_id}")
async def get_employee_templates(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get all templates for an employee"""
    try:
        # Validate employee exists
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
        
        # Get templates
        templates = await template_manager.get_employee_templates(db, employee_id)
        
        template_data = []
        for template in templates:
            template_data.append({
                "template_id": template.id,
                "template_order": template.template_order,
                "created_from": template.created_from,
                "created_at": template.created_at,
                "age_days": template.age_days,
                "quality_score": template.quality_score,
                "confidence_score": template.confidence_score,
                "match_count": template.match_count,
                "avg_match_confidence": template.avg_match_confidence,
                "last_matched": template.last_matched,
                "embedding_size": template.embedding_size,
                "storage_location": "PostgreSQL Database"
            })
        
        return {
            "success": True,
            "employee_id": employee_id,
            "employee_name": employee.full_name,
            "total_templates": len(template_data),
            "templates": template_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee templates: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/stats")
async def get_template_stats(db: Session = Depends(get_db)):
    """Get overall template system statistics"""
    try:
        stats = await template_manager.get_template_stats(db)
        
        return {
            "success": True,
            "statistics": stats,
            "system_info": {
                "max_templates_per_employee": template_manager.MAX_TEMPLATES_PER_EMPLOYEE,
                "replacement_days": template_manager.TEMPLATE_REPLACEMENT_DAYS,
                "min_confidence_threshold": template_manager.MIN_CONFIDENCE_FOR_TEMPLATE,
                "min_quality_threshold": template_manager.MIN_QUALITY_SCORE
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting template stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/employee/{employee_id}/recognition-stats")
async def get_employee_recognition_stats(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get recognition statistics for an employee"""
    try:
        # Validate employee exists
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
        
        stats = await recognition_service.get_employee_recognition_stats(db, employee_id)
        
        if "error" in stats:
            raise HTTPException(status_code=400, detail=stats["error"])
        
        return {
            "success": True,
            "recognition_stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recognition stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/recognize")
async def recognize_face_with_templates(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recognize face using rolling template system
    This is the enhanced recognition endpoint
    """
    try:
        # Decode image
        image_array = decode_image(image)
        
        # Perform recognition
        result = await recognition_service.recognize_face(db, image_array)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in face recognition: {e}")
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")

@router.delete("/template/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific template"""
    try:
        # Get template
        template = db.query(FaceTemplate).filter(FaceTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        # Archive the template (database deletion only)
        db.delete(template)
        db.commit()
        
        logger.info(f"Deleted template {template_id} for employee {template.employee_id} from database")
        
        return {
            "success": True,
            "message": f"Template {template_id} deleted from database successfully",
            "storage_location": "PostgreSQL Database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Deletion error: {str(e)}")

@router.post("/database/cleanup")
async def cleanup_old_templates(
    days_to_keep: int = 30,
    db: Session = Depends(get_db)
):
    """Clean up old templates from database"""
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Count old templates
        old_templates = db.query(FaceTemplate).filter(
            FaceTemplate.created_at < cutoff_date
        ).all()
        
        old_count = len(old_templates)
        
        # Delete old templates
        for template in old_templates:
            db.delete(template)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleaned up {old_count} templates older than {days_to_keep} days from database",
            "templates_removed": old_count,
            "storage_location": "PostgreSQL Database"
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up database: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")

@router.get("/all")
async def get_all_templates(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db)
):
    """Get all templates with pagination"""
    try:
        query = db.query(FaceTemplate).order_by(
            FaceTemplate.employee_id, FaceTemplate.template_order
        )
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        templates = query.all()
        
        template_data = []
        for template in templates:
            # Get employee info
            employee = db.query(Employee).filter(
                Employee.employee_id == template.employee_id
            ).first()
            
            template_data.append({
                "template_id": template.id,
                "employee_id": template.employee_id,
                "employee_name": employee.full_name if employee else "Unknown",
                "template_order": template.template_order,
                "created_from": template.created_from,
                "created_at": template.created_at,
                "age_days": template.age_days,
                "quality_score": template.quality_score,
                "confidence_score": template.confidence_score,
                "match_count": template.match_count,
                "avg_match_confidence": template.avg_match_confidence,
                "last_matched": template.last_matched
            })
        
        total_count = db.query(FaceTemplate).count()
        
        return {
            "success": True,
            "total_count": total_count,
            "returned_count": len(template_data),
            "limit": limit,
            "offset": offset,
            "templates": template_data
        }
        
    except Exception as e:
        logger.error(f"Error getting all templates: {e}")
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@router.put("/settings/thresholds")
async def update_recognition_thresholds(
    recognition_threshold: Optional[float] = None,
    high_confidence_threshold: Optional[float] = None,
    very_high_confidence_threshold: Optional[float] = None
):
    """Update recognition thresholds"""
    try:
        await recognition_service.update_recognition_thresholds(
            recognition_threshold,
            high_confidence_threshold,
            very_high_confidence_threshold
        )
        
        return {
            "success": True,
            "message": "Recognition thresholds updated successfully",
            "current_thresholds": {
                "recognition": recognition_service.RECOGNITION_THRESHOLD,
                "high_confidence": recognition_service.HIGH_CONFIDENCE_THRESHOLD,
                "very_high_confidence": recognition_service.VERY_HIGH_CONFIDENCE_THRESHOLD
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

@router.get("/health")
async def template_system_health():
    """Check template system health"""
    try:
        # Check if services are available
        from app.services.real_ai_service import get_ai_service
        ai_service_available = get_ai_service() is not None
        template_manager_available = template_manager is not None
        recognition_service_available = recognition_service is not None
        
        return {
            "success": True,
            "system_status": "healthy",
            "storage_type": "PostgreSQL Database Only",
            "services": {
                "ai_service": "available" if ai_service_available else "unavailable",
                "template_manager": "available" if template_manager_available else "unavailable",
                "recognition_service": "available" if recognition_service_available else "unavailable"
            },
            "configuration": {
                "max_templates_per_employee": template_manager.MAX_TEMPLATES_PER_EMPLOYEE,
                "replacement_days": template_manager.TEMPLATE_REPLACEMENT_DAYS,
                "recognition_threshold": recognition_service.RECOGNITION_THRESHOLD,
                "storage_location": "PostgreSQL Database"
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return {
            "success": False,
            "system_status": "unhealthy",
            "error": str(e)
        }
