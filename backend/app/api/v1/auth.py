"""
API xác thực thiết bị kiosk
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.device import DeviceCreate
from app.models.device import Device
from app.utils.security import create_access_token

router = APIRouter()

@router.post("/register")
def register_device(device: DeviceCreate, db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.device_id == device.device_id).first()
    if db_device:
        raise HTTPException(status_code=400, detail="Device already registered")
    new_device = Device(
        device_id=device.device_id,
        name=device.name,
        ip_address=device.ip_address,
        token=create_access_token({"device_id": device.device_id, "scope": "kiosk"}),
        is_active=True
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return {"device_id": new_device.device_id, "token": new_device.token}

@router.post("/login")
def login_device(device: DeviceCreate, db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.device_id == device.device_id).first()
    if not db_device or not db_device.is_active:
        raise HTTPException(status_code=401, detail="Device not found or inactive")
    return {"device_id": db_device.device_id, "token": db_device.token}
