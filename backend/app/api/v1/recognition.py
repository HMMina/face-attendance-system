"""
API endpoint for face recognition with enhanced AI models and template system
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.enhanced_recognition_service import get_enhanced_recognition_service
from app.services.real_ai_service import get_ai_service
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize enhanced recognition service
enhanced_recognition_service = get_enhanced_recognition_service()

@router.post("/face")
async def recognize_face(
    image: UploadFile = File(...), 
    device_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Face recognition endpoint using enhanced recognition service
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        camera_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if camera_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Use enhanced recognition service with template system
        result = await enhanced_recognition_service.recognize_face(db, camera_image)
        
        # Add device context
        result["device_id"] = device_id
        
        return result
        
    except Exception as e:
        logger.error(f"Recognition error: {e}")
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")

@router.post("/register")
async def register_face(
    employee_id: str = Form(...),
    image: UploadFile = File(...), 
    device_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Register new face for an employee using enhanced recognition service
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        camera_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if camera_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Use enhanced recognition service for registration
        result = await enhanced_recognition_service.register_face(
            db, camera_image, employee_id, device_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Registration failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.get("/status")
def ai_status():
    """
    Get enhanced recognition service status
    """
    try:
        return enhanced_recognition_service.get_service_status()
    
    except Exception as e:
        logger.error(f"AI status error: {e}")
        return {
            "status": "error",
            "ai_enabled": False,
            "service_type": "enhanced_recognition",
            "error": str(e)
        }

@router.get("/health")
def health_check():
    """
    Enhanced recognition service health check
    """
    try:
        return enhanced_recognition_service.health_check()
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "message": "Enhanced recognition service unavailable"
        }
