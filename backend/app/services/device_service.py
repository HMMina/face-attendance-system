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
    """Get all devices and update network status based on last_seen"""
    devices = db.query(Device).all()
    
    # Update network status based on last_seen (2 minutes timeout)
    current_time = datetime.datetime.utcnow()
    timeout_threshold = current_time - datetime.timedelta(minutes=2)
    
    print(f"🕐 Current time (UTC): {current_time}")
    print(f"🕐 Timeout threshold (UTC): {timeout_threshold} (2 minutes ago)")

    for device in devices:
        if device.last_seen:
            print(f"📱 Device {device.device_id}: last_seen = {device.last_seen} (UTC)")
            
            # Ensure last_seen is treated as UTC if no timezone info
            if device.last_seen.tzinfo is None:
                device_last_seen = device.last_seen
            else:
                device_last_seen = device.last_seen.replace(tzinfo=None)
            
            time_diff = current_time - device_last_seen
            minutes_ago = time_diff.total_seconds() / 60
            print(f"📱 Device {device.device_id}: last seen {minutes_ago:.1f} minutes ago")
            
            # Handle case where last_seen is in the future (timezone issue)
            if minutes_ago < 0:
                print(f"⚠️  Device {device.device_id}: last_seen is in the future! Likely timezone issue. Treating as offline.")
                if device.network_status != "offline":
                    device.network_status = "offline"
                    print(f"🔴 Device {device.device_id} marked as OFFLINE (future timestamp)")
            elif device_last_seen < timeout_threshold:
                # Device should be offline
                if device.network_status != "offline":
                    device.network_status = "offline"
                    print(f"🔴 Device {device.device_id} marked as OFFLINE (last seen: {device.last_seen})")
            else:
                # Device should be online (last seen within 2 minutes)
                if device.network_status != "online":
                    device.network_status = "online"
                    print(f"🟢 Device {device.device_id} marked as ONLINE (last seen: {device.last_seen})")
        else:
            # No last_seen - mark as offline
            if device.network_status != "offline":
                device.network_status = "offline"
                print(f"⚫ Device {device.device_id} marked as OFFLINE (never seen)")
    
    # Commit changes to database
    db.commit()
    
    return devices

def update_heartbeat(db: Session, data: DeviceHeartbeat):
    device = db.query(Device).filter(Device.device_id == data.device_id).first()
    if device:
        # Always use UTC time for consistency
        if hasattr(data, 'timestamp') and data.timestamp:
            # Convert client timestamp to UTC (assume client sends local time UTC+7)
            client_timestamp = data.timestamp
            
            # If timestamp seems to be local time (future compared to UTC), convert it
            current_utc = datetime.datetime.utcnow()
            if client_timestamp > current_utc:
                # Likely local time (UTC+7), convert to UTC
                utc_timestamp = client_timestamp - datetime.timedelta(hours=7)
                print(f"🌏 Converting local time {client_timestamp} to UTC {utc_timestamp}")
                device.last_seen = utc_timestamp
            else:
                # Already UTC or reasonable timestamp
                device.last_seen = client_timestamp
        else:
            # If no timestamp provided, use current UTC time
            device.last_seen = datetime.datetime.utcnow()
            
        device.network_status = "online"  # Always mark as online when heartbeat received
        db.commit()
        print(f"💓 Heartbeat updated for device {data.device_id} - last_seen: {device.last_seen} UTC, status: online")

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
    
    # Delete all attendance records for this device first
    from app.models.attendance import Attendance
    attendance_records = db.query(Attendance).filter(
        Attendance.device_id == db_device.device_id
    ).all()
    
    if attendance_records:
        # Delete attendance records
        for attendance in attendance_records:
            db.delete(attendance)
        db.commit()
        print(f"Deleted {len(attendance_records)} attendance records for device {db_device.device_id}")
    
    # Now safe to delete the device
    db.delete(db_device)
    db.commit()
    return db_device
