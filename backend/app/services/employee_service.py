"""
Employee service functions with proper error handling and class wrapper
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate
from app.utils.id_generator import generate_employee_id, validate_employee_id
import logging

logger = logging.getLogger(__name__)

class EmployeeService:
    """Employee service class with all CRUD operations"""
    
    @staticmethod
    def create_employee(db: Session, employee: EmployeeCreate):
        """Create new employee with validation"""
        try:
            # Auto-generate employee_id if not provided or invalid
            employee_id = employee.employee_id
            if not employee_id or not validate_employee_id(employee_id):
                employee_id = generate_employee_id(db)
                logger.info(f"Auto-generated employee_id: {employee_id}")
            
            # Check if employee_id already exists
            existing = db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Employee ID {employee_id} already exists")
                
            db_employee = Employee(
                employee_id=employee_id,
                name=employee.name,
                department=employee.department,
                email=employee.email,
                phone=employee.phone,
                position=employee.position
            )
            db.add(db_employee)
            db.commit()
            db.refresh(db_employee)
            logger.info(f"Created employee: {employee_id}")
            return db_employee
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {e}")
            raise HTTPException(status_code=400, detail="Employee already exists")
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating employee: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    def get_employees(db: Session, skip: int = 0, limit: int = 100, department: str = None):
        """Get employees with pagination and filtering"""
        try:
            query = db.query(Employee)
            
            # Filter by department if provided
            if department:
                query = query.filter(Employee.department == department)
            
            # Apply pagination and ordering
            return query.order_by(Employee.employee_id.asc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching employees: {e}")
            raise HTTPException(status_code=500, detail="Error fetching employees")

    @staticmethod
    def get_employee(db: Session, employee_id: str):
        """Get employee by ID"""
        try:
            return db.query(Employee).filter(Employee.employee_id == employee_id).first()
        except Exception as e:
            logger.error(f"Error fetching employee {employee_id}: {e}")
            raise HTTPException(status_code=500, detail="Error fetching employee")

    @staticmethod
    def update_employee(db: Session, employee_id: str, employee: EmployeeCreate):
        """Update employee with validation"""
        try:
            db_employee = EmployeeService.get_employee(db, employee_id)
            if not db_employee:
                raise HTTPException(status_code=404, detail="Employee not found")
                
            db_employee.name = employee.name
            db_employee.department = employee.department
            db_employee.email = employee.email
            db_employee.phone = employee.phone
            db_employee.position = employee.position
            db.commit()
            db.refresh(db_employee)
            logger.info(f"Updated employee: {employee_id}")
            return db_employee
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating employee {employee_id}: {e}")
            raise HTTPException(status_code=500, detail="Error updating employee")

    @staticmethod
    def delete_employee(db: Session, employee_id: str):
        """Delete employee"""
        try:
            db_employee = EmployeeService.get_employee(db, employee_id)
            if not db_employee:
                raise HTTPException(status_code=404, detail="Employee not found")
                
            db.delete(db_employee)
            db.commit()
            logger.info(f"Deleted employee: {employee_id}")
            return {"message": "Employee deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting employee {employee_id}: {e}")
            raise HTTPException(status_code=500, detail="Error deleting employee")

# Legacy function wrappers for backward compatibility
def create_employee(db: Session, employee: EmployeeCreate):
    """Legacy function wrapper"""
    return EmployeeService.create_employee(db, employee)

def get_employees(db: Session, skip: int = 0, limit: int = 100, department: str = None):
    """Legacy function wrapper with pagination"""
    return EmployeeService.get_employees(db, skip, limit, department)

def get_employee(db: Session, employee_id: str):
    """Legacy function wrapper"""
    return EmployeeService.get_employee(db, employee_id)

def update_employee(db: Session, employee_id: str, employee: EmployeeCreate):
    """Legacy function wrapper"""
    return EmployeeService.update_employee(db, employee_id, employee)

def delete_employee(db: Session, employee_id: str):
    """Legacy function wrapper"""
    return EmployeeService.delete_employee(db, employee_id)
