"""
API endpoints for employee management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.services.employee_service import create_employee, get_employees, get_employee, update_employee, delete_employee

router = APIRouter()

@router.post("/", response_model=EmployeeOut)
def create(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, employee)

@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return get_employees(db)

@router.get("/{employee_id}", response_model=EmployeeOut)
def get(employee_id: str, db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.put("/{employee_id}", response_model=EmployeeOut)
def update(employee_id: str, employee: EmployeeCreate, db: Session = Depends(get_db)):
    emp = update_employee(db, employee_id, employee)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.delete("/{employee_id}")
def delete(employee_id: str, db: Session = Depends(get_db)):
    emp = delete_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully", "employee_id": employee_id}
