"""
API endpoints for device management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.schemas.device import DeviceCreate, DeviceOut, DeviceHeartbeat
from app.services.device_service import register_device, get_devices, update_heartbeat, get_device_by_id, update_device, delete_device

router = APIRouter()

@router.post("/register", response_model=DeviceOut)
def register(device: DeviceCreate, db: Session = Depends(get_db)):
    return register_device(db, device)

@router.get("/", response_model=List[DeviceOut])
def list_devices(db: Session = Depends(get_db)):
    return get_devices(db)

@router.post("/heartbeat")
def heartbeat(data: DeviceHeartbeat, db: Session = Depends(get_db)):
    update_heartbeat(db, data)
    return {"msg": "Heartbeat updated"}

@router.post("/", response_model=DeviceOut)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    return register_device(db, device)

@router.get("/{device_id}", response_model=DeviceOut)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/{device_id}", response_model=DeviceOut)
def update_device_endpoint(device_id: int, device: DeviceCreate, db: Session = Depends(get_db)):
    updated_device = update_device(db, device_id, device)
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device

@router.delete("/{device_id}")
def delete_device_endpoint(device_id: int, db: Session = Depends(get_db)):
    deleted_device = delete_device(db, device_id)
    if not deleted_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check if device was actually deleted or just deactivated
    if deleted_device.is_active == False and "[DELETED]" in deleted_device.name:
        # Device was deactivated due to attendance records
        return {
            "success": True,
            "message": f"Device {deleted_device.name.replace('[DELETED] ', '')} has been deactivated (has attendance records)",
            "action": "deactivated",
            "device": {
                "id": deleted_device.id,
                "device_id": deleted_device.device_id,
                "name": deleted_device.name,
                "is_active": deleted_device.is_active
            }
        }
    else:
        # Device was completely deleted
        return {
            "success": True,
            "message": f"Device {deleted_device.name} deleted successfully",
            "action": "deleted",
            "device": {
                "id": deleted_device.id,
                "device_id": deleted_device.device_id,
                "name": deleted_device.name
            }
        }

@router.delete("/cleanup/deleted")
def cleanup_deleted_devices(db: Session = Depends(get_db)):
    """Remove all devices marked as [DELETED] from database"""
    from app.models.device import Device
    
    deleted_devices = db.query(Device).filter(
        Device.name.like('[DELETED]%')
    ).all()
    
    cleanup_count = len(deleted_devices)
    
    for device in deleted_devices:
        db.delete(device)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Cleaned up {cleanup_count} deleted devices",
        "cleaned_count": cleanup_count
    }
