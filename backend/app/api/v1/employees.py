"""
API endpoints for employee management
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional
import io
import os
from PIL import Image
import numpy as np
from app.config.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.services.employee_service import create_employee, get_employees, get_employee, update_employee, delete_employee
from app.services.face_embedding_service import FaceEmbeddingService
from app.services.real_ai_service import RealAIService
from app.models.employee import Employee

router = APIRouter()

@router.post("/", response_model=EmployeeOut)
def create(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, employee)

@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return get_employees(db)

@router.get("/departments", response_model=List[str])
def get_departments(db: Session = Depends(get_db)):
    """Get list of unique departments"""
    departments = db.query(distinct(Employee.department)).filter(
        Employee.department.isnot(None),
        Employee.department != ""
    ).all()
    return [dept[0] for dept in departments]

@router.get("/{identifier}", response_model=EmployeeOut)
def get(identifier: str, db: Session = Depends(get_db)):
    # Try to find by database ID first (if it's a number)
    if identifier.isdigit():
        emp = db.query(Employee).filter(Employee.id == int(identifier)).first()
    else:
        # Find by employee_id (string like EMP001)
        emp = get_employee(db, identifier)
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.put("/{identifier}", response_model=EmployeeOut)
def update(identifier: str, employee: EmployeeCreate, db: Session = Depends(get_db)):
    # Try to find by database ID first (if it's a number)
    if identifier.isdigit():
        db_employee = db.query(Employee).filter(Employee.id == int(identifier)).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Update fields
        db_employee.name = employee.name
        db_employee.department = employee.department
        db_employee.email = employee.email
        db_employee.phone = employee.phone
        db_employee.position = employee.position
        
        db.commit()
        db.refresh(db_employee)
        return db_employee
    else:
        # Use employee_id (string like EMP001)
        emp = update_employee(db, identifier, employee)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        return emp

@router.delete("/{identifier}")
def delete(identifier: str, db: Session = Depends(get_db)):
    # Try to find by database ID first (if it's a number)
    if identifier.isdigit():
        db_employee = db.query(Employee).filter(Employee.id == int(identifier)).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee_id = db_employee.employee_id
        db.delete(db_employee)
        db.commit()
        return {"message": "Employee deleted successfully", "employee_id": employee_id}
    else:
        # Use employee_id (string like EMP001)
        emp = delete_employee(db, identifier)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"message": "Employee deleted successfully", "employee_id": identifier}


@router.post("/{identifier}/upload-face")
async def upload_employee_face(
    identifier: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process employee face photo for recognition
    This replaces the need for peripheral device face registration
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Find employee
    if identifier.isdigit():
        employee = db.query(Employee).filter(Employee.id == int(identifier)).first()
    else:
        employee = get_employee(db, identifier)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        # Read image file
        image_bytes = await file.read()
        
        # Convert to numpy array for AI processing
        import io
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            # Fallback for development without AI dependencies
            return {
                "message": "Face upload received (AI dependencies not installed)",
                "employee_id": employee.employee_id,
                "filename": file.filename,
                "size": len(image_bytes)
            }
        
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # Initialize AI service
        ai_service = RealAIService()
        
        # Process face detection and embedding
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
        
        # Save face embedding to database
        embedding_service = FaceEmbeddingService(db)
        embedding_result = await embedding_service.save_embedding(
            employee_id=employee.id,
            embedding_vector=result["embedding"],
            confidence=result.get("confidence", 0.95),
            source="admin_upload",
            metadata={
                "filename": file.filename,
                "upload_method": "admin_panel",
                "file_size": len(image_bytes),
                "image_dimensions": f"{image.width}x{image.height}"
            }
        )
        
        return {
            "message": "Face uploaded and processed successfully",
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "embedding_id": embedding_result.id,
            "confidence": result.get("confidence"),
            "face_quality": result.get("face_quality", "good"),
            "is_primary": embedding_result.is_primary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing face upload: {str(e)}"
        )


@router.get("/{identifier}/face-embeddings")
def get_employee_faces(
    identifier: str,
    db: Session = Depends(get_db)
):
    """
    Get all face embeddings for an employee
    """
    # Find employee
    if identifier.isdigit():
        employee = db.query(Employee).filter(Employee.id == int(identifier)).first()
    else:
        employee = get_employee(db, identifier)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get face embeddings
    from app.models.face_embedding import FaceEmbedding
    embeddings = db.query(FaceEmbedding).filter(
        FaceEmbedding.employee_id == employee.id
    ).all()
    
    return {
        "employee_id": employee.employee_id,
        "employee_name": employee.name,
        "face_count": len(embeddings),
        "faces": [
            {
                "id": emb.id,
                "confidence": emb.confidence,
                "source": emb.source,
                "is_primary": emb.is_primary,
                "created_at": emb.created_at,
                "metadata": emb.metadata
            }
            for emb in embeddings
        ]
    }


@router.delete("/{identifier}/face-embeddings/{embedding_id}")
def delete_employee_face(
    identifier: str,
    embedding_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific face embedding for an employee
    """
    # Find employee
    if identifier.isdigit():
        employee = db.query(Employee).filter(Employee.id == int(identifier)).first()
    else:
        employee = get_employee(db, identifier)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Find and delete embedding
    from app.models.face_embedding import FaceEmbedding
    embedding = db.query(FaceEmbedding).filter(
        FaceEmbedding.id == embedding_id,
        FaceEmbedding.employee_id == employee.id
    ).first()
    
    if not embedding:
        raise HTTPException(status_code=404, detail="Face embedding not found")
    
    db.delete(embedding)
    db.commit()
    
    return {
        "message": "Face embedding deleted successfully",
        "embedding_id": embedding_id,
        "employee_id": employee.employee_id
    }
