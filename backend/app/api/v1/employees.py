"""
API endpoints for employee management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List
from app.config.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.services.employee_service import create_employee, get_employees, get_employee, update_employee, delete_employee
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
