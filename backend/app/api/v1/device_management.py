"""
Device Management API for Multi-Kiosk Testing
API để quản lý và setup các kiosk devices
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.device_setup_service import device_setup_service
from app.services.device_manager import get_device_manager, DeviceManager
from typing import List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class DeviceRegistrationRequest(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    force_update: bool = False

class DeviceUpdateRequest(BaseModel):
    device_name: Optional[str] = None
    is_active: Optional[bool] = None

@router.post("/register")
async def register_device(
    request: DeviceRegistrationRequest,
    client_request: Request,
    db: Session = Depends(get_db),
    device_manager: DeviceManager = Depends(get_device_manager)
):
    """
    Register hoặc update kiosk device
    Dùng để setup device trong quá trình testing
    """
    try:
        client_ip = client_request.client.host if client_request.client else "unknown"
        
        # Register device in database
        result = device_setup_service.register_or_update_device(
            db=db,
            device_id=request.device_id,
            device_name=request.device_name,
            ip_address=client_ip,
            force_update=request.force_update
        )
        
        if result["success"]:
            # Also register in device manager for real-time tracking
            await device_manager.register_device(
                device_id=request.device_id,
                device_name=request.device_name or f"Kiosk_{request.device_id}",
                ip_address=client_ip
            )
            
            logger.info(f"✅ Device registration successful: {request.device_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Device registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_devices(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    device_manager: DeviceManager = Depends(get_device_manager)
):
    """
    List all registered devices với real-time status
    """
    try:
        # Get devices from database
        db_devices = device_setup_service.get_all_devices(db, include_inactive)
        
        # Get real-time status from device manager
        active_devices = device_manager.get_active_devices()
        active_device_ids = {d.device_id for d in active_devices}
        
        # Merge database info với real-time status
        for device in db_devices:
            device["realtime_active"] = device["device_id"] in active_device_ids
            
            # Find matching active device for extra info
            for active_device in active_devices:
                if active_device.device_id == device["device_id"]:
                    device["requests_count"] = active_device.requests_count
                    device["avg_response_time"] = round(active_device.avg_response_time, 3)
                    break
            else:
                device["requests_count"] = 0
                device["avg_response_time"] = 0.0
        
        return {
            "success": True,
            "total_devices": len(db_devices),
            "active_devices": len(active_device_ids),
            "devices": db_devices
        }
        
    except Exception as e:
        logger.error(f"List devices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config/{device_id}")
async def get_device_config(
    device_id: str,
    db: Session = Depends(get_db)
):
    """
    Get device configuration cho kiosk app
    """
    try:
        config = device_setup_service.get_device_config(db, device_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return {
            "success": True,
            "config": config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get device config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{device_id}")
async def update_device(
    device_id: str,
    request: DeviceUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update device settings
    """
    try:
        from app.models.device import Device
        
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Update fields
        if request.device_name is not None:
            device.name = request.device_name
        
        if request.is_active is not None:
            device.is_active = request.is_active
            device.network_status = "online" if request.is_active else "offline"
        
        db.commit()
        db.refresh(device)
        
        return {
            "success": True,
            "message": f"Device {device_id} updated successfully",
            "device": {
                "device_id": device.device_id,
                "name": device.name,
                "is_active": device.is_active,
                "network_status": device.network_status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update device error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/deactivate/{device_id}")
async def deactivate_device(
    device_id: str,
    db: Session = Depends(get_db)
):
    """
    Deactivate device (for testing)
    """
    try:
        success = device_setup_service.deactivate_device(db, device_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return {
            "success": True,
            "message": f"Device {device_id} deactivated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deactivate device error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup-test")
async def cleanup_test_devices(
    prefix: str = "KIOSK_TEST",
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Clean up test devices - use with caution!
    """
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Must set confirm=true to proceed with cleanup"
        )
    
    try:
        count = device_setup_service.cleanup_test_devices(db, prefix)
        
        return {
            "success": True,
            "message": f"Cleaned up {count} test devices with prefix '{prefix}'"
        }
        
    except Exception as e:
        logger.error(f"Cleanup test devices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate-id")
async def generate_device_id():
    """
    Generate unique device ID for testing
    """
    import uuid
    import datetime
    
    timestamp = datetime.datetime.utcnow().strftime("%m%d_%H%M")
    unique_id = str(uuid.uuid4())[:8].upper()
    device_id = f"KIOSK_TEST_{timestamp}_{unique_id}"
    
    return {
        "success": True,
        "device_id": device_id,
        "suggested_name": f"Test Kiosk {timestamp}",
        "note": "Use this ID for testing multiple kiosk instances"
    }
