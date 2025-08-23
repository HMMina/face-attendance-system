"""
API endpoints for employee management with enhanced face embedding system
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
from app.services.enhanced_face_embedding_service import face_embedding_service
from app.models.employee import Employee
from app.models.face_template import FaceTemplate

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
    
    # Count employees with face data using face_templates
    from app.models.face_template import FaceTemplate
    employees_with_faces_query = db.query(FaceTemplate.employee_id).distinct().count()
    employees_with_faces = employees_with_faces_query
    
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
    Upload photo for an existing employee using enhanced face embedding system
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
        
        # Read photo content
        photo_content = await photo.read()
        
        # Prepare photo data for enhanced service
        photos_data = [{
            "filename": photo.filename or f"{employee_id}_avatar.jpg",
            "data": photo_content
        }]
        
        # Process photo using enhanced face embedding service
        processing_results = face_embedding_service.process_employee_photos(
            employee_id, photos_data, selected_avatar_index=0
        )
        
        # Create face templates in database
        if processing_results and processing_results[0].get('success'):
            templates = face_embedding_service.create_face_templates(
                db, employee_id, processing_results
            )
            
            if templates:
                template = templates[0]
                return {
                    "success": True,
                    "message": "Photo uploaded and processed successfully",
                    "employee_id": employee_id,
                    "photo_url": f"/api/v1/employees/{employee_id}/photo",
                    "template_id": template.id,
                    "quality_score": template.quality_score,
                    "confidence_score": template.confidence_score,
                    "embedding_created": True
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create face template")
        else:
            # Photo processed but no face detected
            error_msg = processing_results[0].get('error', 'No face detected') if processing_results else 'Processing failed'
            raise HTTPException(
                status_code=400,
                detail=f"Could not process photo: {error_msg}"
            )
        
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
    Get employee photo from face templates (avatar with image_id=0)
    """
    try:
        # Check if employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get avatar face template (image_id=0)
        face_template = db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id,
            FaceTemplate.image_id == 0
        ).first()
        
        if not face_template or not face_template.image_data:
            raise HTTPException(status_code=404, detail="Avatar photo not found")
        
        # Return the image data
        return Response(
            content=face_template.image_data,
            media_type="image/jpeg",
            headers={"Content-Disposition": f"inline; filename={employee_id}_avatar.jpg"}
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

# ===== NEW ENHANCED FACE EMBEDDING ENDPOINTS =====

@router.post("/{employee_id}/photos/multiple")
async def upload_multiple_photos(
    employee_id: str,
    photos: List[UploadFile] = File(...),
    selected_avatar_index: int = Form(0),
    db: Session = Depends(get_db)
):
    """
    Upload multiple photos for an employee with enhanced embedding system
    - Support up to 4 photos (1 avatar + 3 secondary)
    - image_id 0 = avatar (selected by selected_avatar_index)
    - image_id 1,2,3 = secondary templates
    """
    try:
        # Validate employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Validate input
        if len(photos) > 4:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 4 photos allowed (1 avatar + 3 secondary templates)"
            )
        
        if selected_avatar_index >= len(photos):
            raise HTTPException(
                status_code=400,
                detail=f"selected_avatar_index ({selected_avatar_index}) out of range for {len(photos)} photos"
            )
        
        # Validate all files are images
        for idx, photo in enumerate(photos):
            if not photo.content_type or not photo.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Photo {idx} must be an image (JPEG, PNG, etc.)"
                )
        
        # Prepare photos data
        photos_data = []
        for photo in photos:
            content = await photo.read()
            photos_data.append({
                'filename': photo.filename,
                'data': content
            })
        
        # Process photos with enhanced embedding service
        processing_results = face_embedding_service.process_employee_photos(
            employee_id, photos_data, selected_avatar_index
        )
        
        # Create face templates in database
        face_templates = face_embedding_service.create_face_templates(
            db, employee_id, processing_results
        )
        
        # Prepare response
        successful_results = [r for r in processing_results if r['success']]
        failed_results = [r for r in processing_results if not r['success']]
        
        response_data = {
            'success': True,
            'employee_id': employee_id,
            'total_uploaded': len(photos),
            'successful_processed': len(successful_results),
            'failed_processed': len(failed_results),
            'avatar_image_id': 0,
            'templates_created': len(face_templates),
            'results': []
        }
        
        # Add detailed results
        for result in processing_results:
            if result['success']:
                response_data['results'].append({
                    'index': result['index'],
                    'image_id': result['image_id'],
                    'is_primary': result['is_primary'],
                    'filename': result['filename'],
                    'quality_score': result['quality_score'],
                    'confidence_score': result['confidence_score'],
                    'status': 'success'
                })
            else:
                response_data['results'].append({
                    'index': result['index'],
                    'image_id': result.get('image_id'),
                    'error': result['error'],
                    'status': 'failed'
                })
        
        logger.info(f"Successfully uploaded {len(successful_results)} photos for employee {employee_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error uploading multiple photos for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process photos: {str(e)}")

@router.put("/{employee_id}/photos/update")
async def update_employee_photos(
    employee_id: str,
    photos: List[UploadFile] = File(...),
    selected_avatar_index: int = Form(0),
    db: Session = Depends(get_db)
):
    """
    Update employee photos with rolling template strategy:
    - Keep avatar (image_id=0) if not replaced
    - Replace secondary templates (image_id=1,2,3)
    """
    try:
        # Validate employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Validate input
        if len(photos) > 4:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 4 photos allowed"
            )
        
        if selected_avatar_index >= len(photos):
            raise HTTPException(
                status_code=400,
                detail=f"selected_avatar_index ({selected_avatar_index}) out of range"
            )
        
        # Prepare photos data
        photos_data = []
        for photo in photos:
            if not photo.content_type or not photo.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"All files must be images"
                )
            
            content = await photo.read()
            photos_data.append({
                'filename': photo.filename,
                'data': content
            })
        
        # Update templates using enhanced service
        result = face_embedding_service.update_employee_templates(
            db, employee_id, photos_data, selected_avatar_index
        )
        
        response_data = {
            'success': result['success'],
            'employee_id': employee_id,
            'avatar_updated': result['avatar_updated'],
            'secondary_templates_created': result['secondary_templates_created'],
            'total_templates': result['total_templates'],
            'processing_results': result['processing_results']
        }
        
        logger.info(f"Successfully updated photos for employee {employee_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error updating photos for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update photos: {str(e)}")

@router.get("/{employee_id}/templates")
def get_employee_face_templates(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get all face templates for an employee"""
    try:
        # Validate employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get templates using enhanced service
        templates_info = face_embedding_service.get_employee_templates(db, employee_id)
        
        return templates_info
        
    except Exception as e:
        logger.error(f"Error getting templates for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

@router.get("/{employee_id}/photos/{image_id}")
def get_employee_photo_by_image_id(
    employee_id: str,
    image_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific photo by image_id (0=avatar, 1,2,3=secondary)"""
    try:
        # Get template
        template = db.query(FaceTemplate).filter(
            FaceTemplate.employee_id == employee_id,
            FaceTemplate.image_id == image_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=404, 
                detail=f"Photo with image_id {image_id} not found for employee {employee_id}"
            )
        
        # Check if file exists
        if not os.path.exists(template.file_path):
            raise HTTPException(
                status_code=404,
                detail="Photo file not found on filesystem"
            )
        
        return FileResponse(
            path=template.file_path,
            filename=template.filename,
            media_type='image/jpeg'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting photo for employee {employee_id}, image_id {image_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get photo")

@router.delete("/{employee_id}/photo")
def delete_employee_avatar(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Delete employee avatar (image_id=0) only"""
    try:
        # Validate employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Delete only avatar (image_id=0) using enhanced service
        deleted_count = face_embedding_service.delete_employee_avatar(db, employee_id)
        
        if deleted_count > 0:
            return {
                'success': True,
                'message': f'Avatar deleted for employee {employee_id}',
                'deleted_count': deleted_count
            }
        else:
            return {
                'success': True,
                'message': f'No avatar found for employee {employee_id}',
                'deleted_count': 0
            }
        
    except Exception as e:
        logger.error(f"Error deleting avatar for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete avatar: {str(e)}")

@router.delete("/{employee_id}/photos/all")
def delete_all_employee_photos(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Delete all photos and face templates for an employee"""
    try:
        # Validate employee exists
        employee = get_employee(db, employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Delete using enhanced service
        face_embedding_service.delete_employee_photos(db, employee_id)
        
        return {
            'success': True,
            'message': f'All photos and templates deleted for employee {employee_id}'
        }
        
    except Exception as e:
        logger.error(f"Error deleting photos for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete photos: {str(e)}")
