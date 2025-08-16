"""
Utility functions for ID generation
"""
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.device import Device

def generate_employee_id(db: Session) -> str:
    """Generate next employee ID in format EMP001, EMP002, etc."""
    # Find highest existing employee_id
    employees = db.query(Employee).all()
    
    if not employees:
        return "EMP001"
    
    # Extract numbers from existing IDs
    max_num = 0
    for emp in employees:
        if emp.employee_id and emp.employee_id.startswith("EMP"):
            try:
                num = int(emp.employee_id[3:])  # Remove "EMP" prefix
                max_num = max(max_num, num)
            except ValueError:
                continue
    
    return f"EMP{max_num + 1:03d}"

def generate_device_id(db: Session) -> str:
    """Generate next device ID in format DEV001, DEV002, etc."""
    # Find highest existing device_id
    devices = db.query(Device).all()
    
    if not devices:
        return "DEV001"
    
    # Extract numbers from existing IDs
    max_num = 0
    for dev in devices:
        if dev.device_id and dev.device_id.startswith("DEV"):
            try:
                num = int(dev.device_id[3:])  # Remove "DEV" prefix
                max_num = max(max_num, num)
            except ValueError:
                continue
    
    return f"DEV{max_num + 1:03d}"

def validate_employee_id(employee_id: str) -> bool:
    """Validate employee ID format (EMP followed by 3 digits)"""
    if not employee_id:
        return False
    if not employee_id.startswith("EMP"):
        return False
    if len(employee_id) != 6:
        return False
    try:
        int(employee_id[3:])
        return True
    except ValueError:
        return False

def validate_device_id(device_id: str) -> bool:
    """Validate device ID format (DEV followed by 3 digits)"""
    if not device_id:
        return False
    if not device_id.startswith("DEV"):
        return False
    if len(device_id) != 6:
        return False
    try:
        int(device_id[3:])
        return True
    except ValueError:
        return False
