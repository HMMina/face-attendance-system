"""
API endpoint for face recognition (mock)
"""
from fastapi import APIRouter, UploadFile, File, Form
from app.services.ai_service import mock_recognition

router = APIRouter()

@router.post("/face")
def recognize_face(image: UploadFile = File(...), device_id: str = Form(...)):
    result = mock_recognition(image, device_id)
    return result
