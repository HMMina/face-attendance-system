"""
API endpoint for face recognition with real AI
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.real_ai_service import real_recognition, register_employee_face
from app.services.ai_service import mock_recognition
import os

router = APIRouter()

# Toggle between real AI and mock (set via environment variable)
USE_REAL_AI = os.getenv("USE_REAL_AI", "false").lower() == "true"

@router.post("/face")
async def recognize_face(
    image: UploadFile = File(...), 
    device_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Face recognition endpoint
    """
    try:
        # Read image data
        image_data = await image.read()
        
        if USE_REAL_AI:
            # Use real AI service
            result = real_recognition(image_data, device_id, db)
        else:
            # Use mock service for testing
            result = mock_recognition(image_data, device_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")

@router.post("/register")
async def register_face(
    employee_id: str = Form(...),
    image: UploadFile = File(...), 
    device_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Register new face for an employee
    """
    try:
        # Read image data
        image_data = await image.read()
        
        if USE_REAL_AI:
            # Use real AI service
            result = register_employee_face(image_data, employee_id, device_id, db)
        else:
            # Mock registration
            result = {
                "success": True,
                "message": f"Mock face registration for employee {employee_id}",
                "employee_id": employee_id
            }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.get("/status")
def ai_status():
    """
    Get AI service status
    """
    return {
        "ai_enabled": USE_REAL_AI,
        "service_type": "real_ai" if USE_REAL_AI else "mock",
        "endpoints": [
            "/api/v1/recognition/face",
            "/api/v1/recognition/register",
            "/api/v1/recognition/status"
        ]
    }
