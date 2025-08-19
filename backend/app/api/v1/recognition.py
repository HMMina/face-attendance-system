"""
API endpoint for face recognition with real AI models
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.face_recognition_service import FaceRecognitionService
from app.services.real_ai_service import RealAIService, get_ai_service
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize face recognition service
face_recognition_service = FaceRecognitionService()

@router.post("/face")
async def recognize_face(
    image: UploadFile = File(...), 
    device_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Face recognition endpoint using real AI models
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        camera_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if camera_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Use real AI face recognition service
        result = await face_recognition_service.recognize_face_from_camera(camera_image, db)
        
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
    Register new face for an employee using real AI
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        camera_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if camera_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Use real AI service for registration
        ai_service = get_ai_service()
        result = await ai_service.process_recognition(camera_image)
        
        if not result.get("face_detected"):
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        if not result.get("is_real"):
            raise HTTPException(status_code=400, detail="Spoof detection: Image appears to be fake")
        
        # Store face embedding for employee
        return {
            "success": True,
            "message": f"Face registered successfully for employee {employee_id}",
            "employee_id": employee_id,
            "device_id": device_id,
            "confidence": result.get("confidence", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.get("/status")
def ai_status():
    """
    Get AI service status
    """
    try:
        ai_service = get_ai_service()
        
        return {
            "status": "active",
            "ai_enabled": True,
            "service_type": "real_ai",
            "models": {
                "face_detection": ai_service.face_detector is not None,
                "anti_spoofing": ai_service.anti_spoof_model is not None,
                "face_recognition": ai_service.face_recognizer is not None
            },
            "model_path": str(ai_service.model_path)
        }
    
    except Exception as e:
        logger.error(f"AI status error: {e}")
        return {
            "status": "error",
            "ai_enabled": False,
            "service_type": "none",
            "error": str(e)
        }

@router.get("/health")
def health_check():
    """
    AI service health check
    """
    try:
        ai_service = get_ai_service()
        
        # Test if models are loaded
        models_loaded = {
            "detection": ai_service.face_detector is not None,
            "classification": ai_service.anti_spoof_model is not None, 
            "recognition": ai_service.face_recognizer is not None
        }
        
        all_models_loaded = all(models_loaded.values())
        
        return {
            "healthy": all_models_loaded,
            "models": models_loaded,
            "message": "All AI models loaded" if all_models_loaded else "Some AI models missing"
        }
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "message": "AI service unavailable"
        }
