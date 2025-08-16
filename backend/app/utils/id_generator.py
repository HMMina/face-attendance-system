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
    """Generate next device ID in format KIOSK001, KIOSK002, etc."""
    # Find highest existing device_id
    devices = db.query(Device).all()
    
    if not devices:
        return "KIOSK001"
    
    # Extract numbers from existing IDs (support both KIOSK and DEV for backward compatibility)
    max_num = 0
    for dev in devices:
        if dev.device_id:
            if dev.device_id.startswith("KIOSK"):
                try:
                    num = int(dev.device_id[5:])  # Remove "KIOSK" prefix
                    max_num = max(max_num, num)
                except ValueError:
                    continue
            elif dev.device_id.startswith("DEV"):
                try:
                    num = int(dev.device_id[3:])  # Remove "DEV" prefix  
                    max_num = max(max_num, num)
                except ValueError:
                    continue
    
    return f"KIOSK{max_num + 1:03d}"

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
    """Validate device ID format (KIOSK followed by 3 digits, or DEV for backward compatibility)"""
    if not device_id:
        return False
    
    # Support both KIOSK001 and DEV001 formats
    if device_id.startswith("KIOSK"):
        if len(device_id) != 8:  # KIOSK + 3 digits = 8 chars
            return False
        try:
            int(device_id[5:])  # Extract number part after "KIOSK"
            return True
        except ValueError:
            return False
    elif device_id.startswith("DEV"):
        if len(device_id) != 6:  # DEV + 3 digits = 6 chars
            return False
        try:
            int(device_id[3:])  # Extract number part after "DEV"
            return True
        except ValueError:
            return False
    else:
        return False
