"""
API lấy lịch sử chấm công và nhận batch dữ liệu offline
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceOut
import datetime
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = './data/uploads/faces/originals/'

@router.post("/check")
async def check_attendance(
    image: UploadFile = File(...),
    device_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint cho kiosk app để gửi ảnh và nhận kết quả chấm công
    """
    try:
        # Validate image
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Use real AI face recognition
        from app.services.face_recognition_service import FaceRecognitionService
        import cv2
        import numpy as np
        
        face_recognition_service = FaceRecognitionService()
        
        # Convert uploaded image to OpenCV format
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        camera_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if camera_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Save image first
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        timestamp = datetime.datetime.now()
        file_path = os.path.join(UPLOAD_DIR, f"attendance_{device_id}_{timestamp.isoformat()}.jpg")
        
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Real face recognition
        recognition_result = await face_recognition_service.recognize_face_from_camera(camera_image, db)
        
        if not recognition_result.get("recognized", False):
            # Unknown person - save as unrecognized attendance
            attendance = Attendance(
                employee_id="UNKNOWN",
                device_id=device_id,
                confidence=0.0,
                image_path=file_path,
                timestamp=timestamp,
                action_type="UNRECOGNIZED"
            )
            db.add(attendance)
            db.commit()
            db.refresh(attendance)
            
            return {
                "success": False,
                "message": "Person not recognized",
                "attendance_id": attendance.id,
                "timestamp": timestamp.isoformat(),
                "confidence": 0.0
            }
        
        # Recognized person - get employee details
        employee_id = recognition_result.get("employee_id")
        employee_name = recognition_result.get("employee_name")
        confidence = recognition_result.get("confidence", 0.0)
        
        # Save attendance record
        attendance = Attendance(
            employee_id=employee_id,
            device_id=device_id,
            confidence=confidence,
            image_path=file_path,
            timestamp=timestamp,
            action_type="RECOGNIZED"
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        logger.info(f"Attendance recorded for employee {employee_id} from device {device_id}")
        
        return {
            "success": True,
            "employee_id": employee_id,
            "employee_name": employee_name,
            "confidence": confidence,
            "timestamp": timestamp.isoformat(),
            "attendance_id": attendance.id
        }
        
    except Exception as e:
        logger.error(f"Error in attendance check: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/upload")
def upload_attendance(
    image: UploadFile = File(...),
    employee_id: str = Form(...),
    device_id: str = Form(...),
    confidence: float = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Lưu ảnh gốc
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, f"{employee_id}_{datetime.datetime.now().isoformat()}.jpg")
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        # Lưu attendance
        att = Attendance(
            employee_id=employee_id,
            device_id=device_id,
            confidence=confidence,
            image_path=file_path,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(att)
        db.commit()
        db.refresh(att)
        return {"success": True, "attendance_id": att.id}
    except Exception as e:
        logger.error(f"Error uploading attendance: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
def batch_attendance(data: list[dict], db: Session = Depends(get_db)):
    # Nhận batch dữ liệu offline từ thiết bị
    for item in data:
        att = Attendance(
            employee_id=item.get('employee_id'),
            device_id=item.get('device_id'),
            confidence=item.get('confidence', 0.0),
            image_path=item.get('image_path', ''),
            timestamp=datetime.datetime.fromisoformat(item.get('timestamp'))
        )
        db.add(att)
    db.commit()
    return {"success": True, "count": len(data)}

@router.get("/history/{device_id}", response_model=list[AttendanceOut])
def get_attendance_history(device_id: str, db: Session = Depends(get_db)):
    return db.query(Attendance).filter(Attendance.device_id == device_id).order_by(Attendance.timestamp.desc()).all()

@router.get("/employee/{employee_id}", response_model=list[AttendanceOut])
def get_employee_attendance(employee_id: str, db: Session = Depends(get_db)):
    return db.query(Attendance).filter(Attendance.employee_id == employee_id).order_by(Attendance.timestamp.desc()).all()

@router.get("/", response_model=list[AttendanceOut])
def get_all_attendance(db: Session = Depends(get_db)):
    return db.query(Attendance).order_by(Attendance.timestamp.desc()).all()
