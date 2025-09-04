"""
API lấy lịch sử chấm công và nhận batch dữ liệu offline - Multi-Kiosk Optimized
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceOut
from app.services.device_manager import get_device_manager, DeviceManager
from app.config.multi_kiosk_config_fixed import get_device_upload_path
import datetime
import os
import logging
import time
import asyncio

def format_vietnam_time(utc_datetime):
    """Convert UTC datetime to Vietnam timezone (UTC+7) and format"""
    vietnam_time = utc_datetime + datetime.timedelta(hours=7)
    return vietnam_time.strftime("%H:%M - %d/%m/%Y")

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = './data/uploads/faces/originals/'

@router.post("/check")
async def check_attendance(
    request: Request,
    image: UploadFile = File(...),
    device_id: str = Form(...),
    attendance_type: str = Form(default="IN"),  # Frontend gửi IN/OUT
    db: Session = Depends(get_db),
    device_manager: DeviceManager = Depends(get_device_manager)
):
    """
    Multi-Kiosk Optimized Endpoint cho kiosk app để gửi ảnh và nhận kết quả chấm công
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # 1. Register/Update device in system
        await device_manager.register_device(
            device_id=device_id,
            device_name=f"Kiosk_{device_id}",
            ip_address=client_ip
        )
        
        # 2. Get device-specific lock to prevent concurrent processing
        device_lock = await device_manager.get_device_lock(device_id)
        
        async with device_lock:
            # Debug logging
            logger.info(f"🎯 Processing request from device {device_id} at {client_ip}")
            logger.info(f"📝 Attendance type received: {attendance_type}")
            logger.info(f"Received file: {image.filename}")
            logger.info(f"Content type: {image.content_type}")
            logger.info(f"File size: {image.size if hasattr(image, 'size') else 'Unknown'}")
            
            # Validate image - allow files without content type or with image content type
            if image.content_type and not image.content_type.startswith('image/'):
                logger.error(f"Invalid content type: {image.content_type}")
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # If no content type, try to validate by reading the file
            if not image.content_type:
                logger.warning("No content type provided, will validate by file content")
            
            # Use enhanced face recognition with template system
            from app.services.enhanced_recognition_service import get_enhanced_recognition_service
            import cv2
            import numpy as np
            
            enhanced_recognition_service = get_enhanced_recognition_service()
            
            # Convert uploaded image to OpenCV format
            image_data = await image.read()
            nparr = np.frombuffer(image_data, np.uint8)
            camera_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if camera_image is None:
                raise HTTPException(status_code=400, detail="Invalid image format")
            
            # Save image to device-specific directory
            device_upload_dir = get_device_upload_path(device_id, UPLOAD_DIR)
            os.makedirs(device_upload_dir, exist_ok=True)
            
            timestamp = datetime.datetime.utcnow()
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
            file_path = os.path.join(device_upload_dir, f"attendance_{device_id}_{timestamp_str}.jpg")
            
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # Enhanced face recognition with template learning
            recognition_result = await enhanced_recognition_service.recognize_face(db, camera_image)
        
        # DEBUG: Always get employee info if available
        employee_info = recognition_result.get("employee")
        employee_id = recognition_result.get("employee_id")
        similarity = recognition_result.get("similarity", 0.0)
        threshold = recognition_result.get("thresholds", {}).get("recognition", 0.65)
        
        # Check if we have employee data to return
        if employee_info and employee_id:
            # We found a match - determine if it's good enough for attendance logging
            meets_threshold = recognition_result.get("recognized", False)
            
            if meets_threshold:
                # High confidence - log attendance
                logger.info(f"✅ High confidence recognition: {employee_id} with similarity {similarity:.3f}")
                
                # Get full employee information for attendance logging
                from app.services.employee_service import get_employee
                employee = get_employee(db, employee_id)
                
                # Convert frontend attendance_type (IN/OUT) to database action_type (CHECK_IN/CHECK_OUT)
                action_type = "CHECK_IN" if attendance_type.upper() == "IN" else "CHECK_OUT"
                
                # Save attendance record (remove fields not in model)
                attendance = Attendance(
                    employee_id=employee_id,
                    device_id=device_id,
                    confidence=similarity,
                    timestamp=timestamp,
                    image_path=file_path,
                    action_type=action_type  # Use converted action_type
                )
                db.add(attendance)
                db.commit()
                db.refresh(attendance)
                
                return {
                    "success": True,
                    "message": "Chấm công thành công!",
                    "employee": employee_info,
                    "attendance_id": attendance.id,
                    "timestamp": timestamp.isoformat(),
                    "formatted_time": format_vietnam_time(timestamp),
                    "confidence": similarity,
                    "similarity": similarity,
                    "recognition_details": {
                        "confidence_level": recognition_result.get("confidence_level", "HIGH"),
                        "template_id": recognition_result.get("template_id"),
                        "is_primary": recognition_result.get("is_primary", False)
                    }
                }
            else:
                # Low confidence - DON'T log attendance and return failure
                logger.info(f"🔍 DEBUG: Low confidence match: {employee_id} with similarity {similarity:.3f}")
                return {
                    "success": False,  # ✅ CHANGED: Return False for low confidence
                    "message": "Khuôn mặt không đạt độ tin cậy cần thiết để chấm công",
                    "timestamp": timestamp.isoformat(),
                    "formatted_time": format_vietnam_time(timestamp),
                    "confidence": similarity,
                    "similarity": similarity,
                    "recognition_details": {
                        "confidence_level": recognition_result.get("confidence_level", "LOW"),
                        "best_similarity": similarity,
                        "threshold_met": False,
                        "employee_found": True,
                        "employee_id": employee_id,
                        "threshold_required": threshold
                    }
                }
        
        # No match found at all
        if not recognition_result.get("recognized", False):
            # Unknown person - only save image
            logger.warning(f"Face not recognized for device {device_id}, image saved at {file_path}")
            response_data = {
                "success": False,
                "message": recognition_result.get("message", "Person not recognized"),
                "timestamp": timestamp.isoformat(),
                "confidence": 0.0,
                "image_path": file_path,
                "device_id": device_id,
                "recognition_details": {
                    "best_similarity": recognition_result.get("best_similarity", 0.0),
                    "confidence_level": "NONE"
                }
            }
        
        # Update device statistics
        processing_time = time.time() - start_time
        await device_manager.update_device_stats(device_id, processing_time)
        
        # Add performance metrics to response
        if "response_data" not in locals():
            response_data = {}
        response_data["performance"] = {
            "processing_time": round(processing_time, 3),
            "device_id": device_id,
            "timestamp": timestamp.isoformat()
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in attendance check for device {device_id}: {e}")
        db.rollback()
        
        # Still update device stats on error
        processing_time = time.time() - start_time
        await device_manager.update_device_stats(device_id, processing_time)
        
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
        timestamp_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        file_path = os.path.join(UPLOAD_DIR, f"{employee_id}_{timestamp_str}.jpg")
        image_data = image.file.read() if hasattr(image.file, 'read') else image.read()
        with open(file_path, "wb") as f:
            f.write(image_data)
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
