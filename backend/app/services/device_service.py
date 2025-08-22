"""
Business logic for device management
"""
from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceHeartbeat
from app.utils.id_generator import generate_device_id, validate_device_id
import datetime
import secrets

def register_device(db: Session, device: DeviceCreate):
    # Auto-generate device_id if not provided or invalid
    device_id = device.device_id
    if not device_id or not validate_device_id(device_id):
        device_id = generate_device_id(db)
    
    db_device = Device(
        device_id=device_id,
        name=device.name,
        ip_address=device.ip_address,
        token=secrets.token_hex(16),
        registered_at=datetime.datetime.utcnow(),
        last_seen=datetime.datetime.utcnow(),
        is_active=True,
        network_status="online"
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_devices(db: Session):
    return db.query(Device).all()

def update_heartbeat(db: Session, data: DeviceHeartbeat):
    device = db.query(Device).filter(Device.device_id == data.device_id).first()
    if device:
        device.last_seen = data.timestamp
        device.network_status = data.network_status
        db.commit()

def get_device_by_id(db: Session, device_id: int):
    return db.query(Device).filter(Device.id == device_id).first()

def update_device(db: Session, device_id: int, device_data: DeviceCreate):
    db_device = get_device_by_id(db, device_id)
    if not db_device:
        return None
    
    # Update all fields that can be modified
    if device_data.name is not None:
        db_device.name = device_data.name
    if device_data.ip_address is not None:
        db_device.ip_address = device_data.ip_address
    if device_data.device_id is not None:
        db_device.device_id = device_data.device_id
    if device_data.is_active is not None:
        db_device.is_active = device_data.is_active
    
    # Update last_seen to current time
    db_device.last_seen = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int):
    db_device = get_device_by_id(db, device_id)
    if not db_device:
        return None
    db.delete(db_device)
    db.commit()
    return db_device
