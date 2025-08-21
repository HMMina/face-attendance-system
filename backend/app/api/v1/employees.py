"""
API endpoints for employee management
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional
import io
import os
import logging
from PIL import Image
import numpy as np
from app.config.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.services.employee_service import create_employee, get_employees, get_employee, update_employee, delete_employee
from app.services.face_embedding_service import FaceEmbeddingService
from app.services.real_ai_service import RealAIService
from app.services.employee_photo_service import photo_service
from app.models.employee import Employee

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=EmployeeOut)
def create_employee_endpoint(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    return create_employee(db, employee)

@router.post("/with-photo", response_model=dict)
async def create_employee_with_photo(
    name: str = Form(...),
    department: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    employee_id: Optional[str] = Form(None),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Create a new employee with photo upload
    This combines employee creation with local photo storage
    """
    try:
        # Validate photo file
        if not photo.content_type or not photo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Create employee data
        employee_data = EmployeeCreate(
            employee_id=employee_id,
            name=name,
            department=department,
            email=email,
            phone=phone,
            position=position
        )
        
        # Create employee in database
        new_employee = create_employee(db, employee_data)
        
        try:
            # Read and process photo
            photo_content = await photo.read()
            image = Image.open(io.BytesIO(photo_content))
            
            # Save photo locally
            photo_info = photo_service.save_employee_photo(
                employee_id=new_employee.employee_id,
                image_file=image,
                original_filename=photo.filename
            )
            
            # Use local photo for face recognition processing
            ai_service = RealAIService()
            
            # Convert to numpy array for AI processing
            image_array = np.array(image)
            
            # Process with AI
            result = await ai_service.process_recognition(image_array)
            
            # Store face embedding if face detected
            face_embedding_id = None
            if result.get("face_detected") and result.get("embedding") is not None:
                face_service = FaceEmbeddingService(db)
                face_embedding_id = face_service.store_face_embedding(
                    employee_id=new_employee.employee_id,
                    embedding=result.get("embedding"),
                    metadata={
                        "photo_id": photo_info["photo_id"],
                        "upload_timestamp": result.get("timestamp"),
                        "face_quality": result.get("face_quality", 0.0),
                        "detection_confidence": result.get("detection_confidence", 0.0),
                        "model_version": result.get("model_version", "unknown"),
                        "local_photo_path": photo_info["processed_path"]
                    }
                )
            
            return {
                "message": "Employee created successfully with photo",
                "employee": {
                    "id": new_employee.id,
                    "employee_id": new_employee.employee_id,
                    "name": new_employee.name,
                    "department": new_employee.department,
                    "email": new_employee.email,
                    "phone": new_employee.phone,
                    "position": new_employee.position
                },
                "photo": {
                    "photo_id": photo_info["photo_id"],
                    "stored_locally": True,
                    "local_path": photo_info["processed_path"],
                    "thumbnail_path": photo_info["thumbnail_path"],
                    "file_size": photo_info["file_size"],
                    "dimensions": photo_info["dimensions"]
                },
                "face_recognition": {
                    "face_detected": result.get("face_detected", False),
                    "face_quality": result.get("face_quality", 0.0),
                    "embedding_stored": face_embedding_id is not None,
                    "embedding_id": face_embedding_id,
                    "processing_time": result.get("processing_time", 0.0)
                }
            }
            
        except Exception as photo_error:
            # If photo processing fails, we still have the employee created
            # We can try to process the photo later
            logger.warning(f"Photo processing failed for employee {new_employee.employee_id}: {photo_error}")
            
            return {
                "message": "Employee created but photo processing failed",
                "employee": {
                    "id": new_employee.id,
                    "employee_id": new_employee.employee_id,
                    "name": new_employee.name,
                    "department": new_employee.department,
                    "email": new_employee.email,
                    "phone": new_employee.phone,
                    "position": new_employee.position
                },
                "photo": {
                    "stored_locally": False,
                    "error": str(photo_error)
                },
                "face_recognition": {
                    "face_detected": False,
                    "embedding_stored": False
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating employee with photo: {str(e)}"
        )

@router.get("/", response_model=List[EmployeeOut])
def get_employees_endpoint(
    skip: int = 0, 
    limit: int = 100, 
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all employees with optional filtering"""
    return get_employees(db, skip=skip, limit=limit, department=department)

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    """Get list of all departments"""
    departments = db.query(distinct(Employee.department)).filter(
        Employee.department.isnot(None)
    ).all()
    
    return {
        "departments": [dept[0] for dept in departments if dept[0]]
    }

@router.get("/stats")
def get_employee_stats(db: Session = Depends(get_db)):
    """Get employee statistics"""
    total_employees = db.query(Employee).count()
    
    # Count employees by department
    dept_counts = db.query(
        Employee.department, 
        db.func.count(Employee.id)
    ).group_by(Employee.department).all()
    
    # Count employees with face data
    face_service = FaceEmbeddingService(db)
    employees_with_faces = len(face_service.get_all_employee_ids_with_embeddings())
    
    return {
        "total_employees": total_employees,
        "employees_with_faces": employees_with_faces,
        "employees_without_faces": total_employees - employees_with_faces,
        "departments": {
            dept: count for dept, count in dept_counts if dept
        }
    }

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee_endpoint(employee_id: str, db: Session = Depends(get_db)):
    """Get a specific employee by ID"""
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee_endpoint(
    employee_id: str, 
    employee: EmployeeCreate, 
    db: Session = Depends(get_db)
):
    """Update an employee"""
    updated_employee = update_employee(db, employee_id, employee)
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee

@router.post("/{employee_id}/upload-photo")
async def upload_employee_photo(
    employee_id: str,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload photo for an existing employee
    """
    try:
        # Check if employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Validate photo file
        if not photo.content_type or not photo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read and process photo
        photo_content = await photo.read()
        image = Image.open(io.BytesIO(photo_content))
        
        # Save photo to backend/data/employee_photos/
        import os
        photos_dir = os.path.join(os.path.dirname(__file__), "../../../data/employee_photos")
        os.makedirs(photos_dir, exist_ok=True)
        
        # Save original photo
        photo_filename = f"{employee_id}.jpg"
        photo_path = os.path.join(photos_dir, photo_filename)
        
        # Convert to RGB if necessary and save
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        image.save(photo_path, "JPEG", quality=85)
        
        # Update employee record with photo path
        from sqlalchemy import update
        db.execute(
            update(Employee)
            .where(Employee.employee_id == employee_id)
            .values(photo_path=f"/api/v1/employees/{employee_id}/photo")
        )
        db.commit()
        
        return {
            "message": "Photo uploaded successfully",
            "employee_id": employee_id,
            "photo_path": photo_path,
            "photo_url": f"/api/v1/employees/{employee_id}/photo",
            "file_size": len(photo_content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading photo: {str(e)}"
        )

@router.get("/{employee_id}/photo")
async def get_employee_photo(employee_id: str, db: Session = Depends(get_db)):
    """
    Get employee photo
    """
    try:
        # Check if employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if photo exists
        import os
        photos_dir = os.path.join(os.path.dirname(__file__), "../../../data/employee_photos")
        photo_path = os.path.join(photos_dir, f"{employee_id}.jpg")
        
        if not os.path.exists(photo_path):
            raise HTTPException(status_code=404, detail="Photo not found")
        
        return FileResponse(
            photo_path,
            media_type="image/jpeg",
            filename=f"{employee_id}.jpg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting photo for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting photo: {str(e)}"
        )

@router.delete("/{employee_id}")
def delete_employee_endpoint(employee_id: str, db: Session = Depends(get_db)):
    """Delete an employee"""
    success = delete_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}

@router.post("/{employee_id}/upload-face")
async def upload_face(
    employee_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process face image for an employee with enhanced AI validation
    """
    # Validate employee exists
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    try:
        # Read image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for AI processing
        image_array = np.array(image)
        
        # Process face detection and embedding with enhanced AI
        ai_service = RealAIService()
        
        # Use optimized async processing
        result = await ai_service.process_recognition(image_array)
        
        if not result.get("face_detected"):
            raise HTTPException(
                status_code=400, 
                detail="No face detected in the uploaded image. Please upload a clear photo with visible face."
            )
        
        if not result.get("is_real"):
            raise HTTPException(
                status_code=400,
                detail="Possible spoof detected. Please upload a real photo, not a screen or printed image."
            )
        
        # Enhanced quality check
        quality_score = result.get("face_quality", 0.0)
        if quality_score < 0.3:
            quality_issues = result.get("quality_issues", [])
            issues_text = ", ".join(quality_issues) if quality_issues else "low quality"
            raise HTTPException(
                status_code=400,
                detail=f"Image quality too low ({issues_text}). Please upload a clearer photo."
            )
        
        # Get face embedding
        face_embedding = result.get("embedding")
        if face_embedding is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract face embedding. Please try again."
            )
        
        # Store face embedding
        face_service = FaceEmbeddingService(db)
        embedding_id = face_service.store_face_embedding(
            employee_id=employee_id,
            embedding=face_embedding,
            metadata={
                "upload_timestamp": result.get("timestamp"),
                "face_quality": quality_score,
                "detection_confidence": result.get("detection_confidence", 0.0),
                "model_version": result.get("model_version", "unknown"),
                "image_size": f"{image.width}x{image.height}",
                "preprocessing": result.get("preprocessing_applied", [])
            }
        )
        
        return {
            "message": "Face uploaded and processed successfully",
            "employee_id": employee_id,
            "embedding_id": embedding_id,
            "face_quality": quality_score,
            "detection_confidence": result.get("detection_confidence", 0.0),
            "processing_time": result.get("processing_time", 0.0),
            "model_info": result.get("model_info", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing face upload: {str(e)}"
        )

@router.get("/{employee_id}/photos")
def get_employee_photos_endpoint(employee_id: str, db: Session = Depends(get_db)):
    """Get all local photos for an employee"""
    # Verify employee exists
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    photos = photo_service.get_employee_photos(employee_id)
    
    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "total_photos": len(photos),
        "photos": photos
    }

@router.get("/{employee_id}/photos/{photo_id}/thumbnail")
async def get_photo_thumbnail(employee_id: str, photo_id: str, db: Session = Depends(get_db)):
    """Get thumbnail of employee photo"""
    # Verify employee exists
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    photos = photo_service.get_employee_photos(employee_id)
    photo = next((p for p in photos if p["photo_id"] == photo_id), None)
    
    if not photo or not photo.get("thumbnail_path"):
        raise HTTPException(status_code=404, detail="Photo thumbnail not found")
    
    if not os.path.exists(photo["thumbnail_path"]):
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    return FileResponse(
        photo["thumbnail_path"],
        media_type="image/jpeg",
        filename=f"{employee_id}_{photo_id}_thumb.jpg"
    )

@router.get("/{employee_id}/photos/{photo_id}/download")
async def download_employee_photo(employee_id: str, photo_id: str, db: Session = Depends(get_db)):
    """Download original employee photo"""
    # Verify employee exists
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    photos = photo_service.get_employee_photos(employee_id)
    photo = next((p for p in photos if p["photo_id"] == photo_id), None)
    
    if not photo or not photo.get("original_path"):
        raise HTTPException(status_code=404, detail="Photo not found")
    
    if not os.path.exists(photo["original_path"]):
        raise HTTPException(status_code=404, detail="Photo file not found")
    
    return FileResponse(
        photo["original_path"],
        media_type="image/jpeg",
        filename=f"{employee_id}_{photo_id}_original.jpg"
    )

@router.delete("/{employee_id}/photos/{photo_id}")
def delete_employee_photo_endpoint(employee_id: str, photo_id: str, db: Session = Depends(get_db)):
    """Delete a specific employee photo"""
    # Verify employee exists
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    success = photo_service.delete_employee_photo(employee_id, photo_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return {"message": f"Photo {photo_id} deleted successfully"}

@router.post("/{employee_id}/photos/upload")
async def upload_additional_photo(
    employee_id: str,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload additional photo for existing employee"""
    # Verify employee exists
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Validate photo file
    if not photo.content_type or not photo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    try:
        # Read and process photo
        photo_content = await photo.read()
        image = Image.open(io.BytesIO(photo_content))
        
        # Save photo locally
        photo_info = photo_service.save_employee_photo(
            employee_id=employee_id,
            image_file=image,
            original_filename=photo.filename
        )
        
        # Process with AI for face recognition
        ai_service = RealAIService()
        image_array = np.array(image)
        result = await ai_service.process_recognition(image_array)
        
        # Store face embedding if face detected
        face_embedding_id = None
        if result.get("face_detected") and result.get("embedding") is not None:
            face_service = FaceEmbeddingService(db)
            face_embedding_id = face_service.store_face_embedding(
                employee_id=employee_id,
                embedding=result.get("embedding"),
                metadata={
                    "photo_id": photo_info["photo_id"],
                    "upload_timestamp": result.get("timestamp"),
                    "face_quality": result.get("face_quality", 0.0),
                    "detection_confidence": result.get("detection_confidence", 0.0),
                    "local_photo_path": photo_info["processed_path"]
                }
            )
        
        return {
            "message": "Photo uploaded successfully",
            "employee_id": employee_id,
            "photo": {
                "photo_id": photo_info["photo_id"],
                "stored_locally": True,
                "local_path": photo_info["processed_path"],
                "thumbnail_path": photo_info["thumbnail_path"],
                "file_size": photo_info["file_size"],
                "dimensions": photo_info["dimensions"]
            },
            "face_recognition": {
                "face_detected": result.get("face_detected", False),
                "face_quality": result.get("face_quality", 0.0),
                "embedding_stored": face_embedding_id is not None,
                "embedding_id": face_embedding_id,
                "processing_time": result.get("processing_time", 0.0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading photo: {str(e)}"
        )

@router.delete("/{employee_id}/faces/{embedding_id}")
def delete_employee_face(
    employee_id: str, 
    embedding_id: int, 
    db: Session = Depends(get_db)
):
    """Delete a specific face embedding for an employee"""
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    face_service = FaceEmbeddingService(db)
    success = face_service.delete_embedding(embedding_id, employee_id)
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Face embedding not found or doesn't belong to this employee"
        )
    
    return {"message": "Face embedding deleted successfully"}
def get_employee_stats(db: Session = Depends(get_db)):
    """Get employee statistics"""
    total_employees = db.query(Employee).count()
    
    # Count employees by department
    dept_counts = db.query(
        Employee.department, 
        db.func.count(Employee.id)
    ).group_by(Employee.department).all()
    
    # Count employees with face data
    face_service = FaceEmbeddingService(db)
    employees_with_faces = len(face_service.get_all_employee_ids_with_embeddings())
    
    return {
        "total_employees": total_employees,
        "employees_with_faces": employees_with_faces,
        "employees_without_faces": total_employees - employees_with_faces,
        "departments": {
            dept: count for dept, count in dept_counts if dept
        }
    }
