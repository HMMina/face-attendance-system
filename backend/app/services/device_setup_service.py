"""
Device Registration & Setup Service for Multi-Kiosk Testing
Quản lý setup và registration của các kiosk devices
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.device import Device
from app.config.database import get_db
from typing import Dict, List, Optional
import datetime
import secrets
import logging

logger = logging.getLogger(__name__)

class DeviceSetupService:
    """Service for setting up and managing kiosk devices"""
    
    @staticmethod
    def register_or_update_device(
        db: Session, 
        device_id: str, 
        device_name: str = None,
        ip_address: str = None,
        force_update: bool = False
    ) -> Dict:
        """
        Register new device hoặc update existing device
        Tự động generate token và update thông tin
        """
        try:
            # Tìm device existing
            existing_device = db.query(Device).filter(Device.device_id == device_id).first()
            
            if existing_device and not force_update:
                # Update last_seen và ip_address nếu có
                existing_device.last_seen = datetime.datetime.utcnow()
                existing_device.is_active = True
                existing_device.network_status = "online"
                
                if ip_address:
                    existing_device.ip_address = ip_address
                
                db.commit()
                db.refresh(existing_device)
                
                logger.info(f"📱 Updated existing device: {device_id}")
                return {
                    "success": True,
                    "action": "updated",
                    "device": {
                        "device_id": existing_device.device_id,
                        "name": existing_device.name,
                        "token": existing_device.token,
                        "registered_at": existing_device.registered_at.isoformat(),
                        "last_seen": existing_device.last_seen.isoformat(),
                        "ip_address": existing_device.ip_address,
                        "is_active": existing_device.is_active
                    }
                }
            
            else:
                # Create new device hoặc force update
                if existing_device:
                    # Force update
                    device = existing_device
                    logger.info(f"🔄 Force updating device: {device_id}")
                else:
                    # Create new
                    device = Device()
                    logger.info(f"🆕 Creating new device: {device_id}")
                
                # Set/update properties
                device.device_id = device_id
                device.name = device_name or f"Kiosk_{device_id}"
                device.ip_address = ip_address
                device.token = secrets.token_urlsafe(32)
                device.last_seen = datetime.datetime.utcnow()
                device.registered_at = datetime.datetime.utcnow() if not existing_device else device.registered_at
                device.is_active = True
                device.network_status = "online"
                
                if not existing_device:
                    db.add(device)
                
                db.commit()
                db.refresh(device)
                
                return {
                    "success": True,
                    "action": "created" if not existing_device else "force_updated",
                    "device": {
                        "device_id": device.device_id,
                        "name": device.name,
                        "token": device.token,
                        "registered_at": device.registered_at.isoformat(),
                        "last_seen": device.last_seen.isoformat(),
                        "ip_address": device.ip_address,
                        "is_active": device.is_active
                    }
                }
                
        except Exception as e:
            logger.error(f"Error registering device {device_id}: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_all_devices(db: Session, include_inactive: bool = False) -> List[Dict]:
        """Get all devices, optionally including inactive ones"""
        try:
            query = db.query(Device)
            
            if not include_inactive:
                query = query.filter(Device.is_active == True)
            
            devices = query.order_by(Device.last_seen.desc()).all()
            
            return [
                {
                    "device_id": device.device_id,
                    "name": device.name,
                    "registered_at": device.registered_at.isoformat() if device.registered_at else None,
                    "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                    "ip_address": device.ip_address,
                    "is_active": device.is_active,
                    "network_status": device.network_status,
                    "token_preview": device.token[:8] + "..." if device.token else None
                }
                for device in devices
            ]
            
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return []
    
    @staticmethod
    def get_device_config(db: Session, device_id: str) -> Optional[Dict]:
        """Get device configuration for kiosk app"""
        try:
            device = db.query(Device).filter(Device.device_id == device_id).first()
            
            if not device:
                return None
            
            return {
                "device_id": device.device_id,
                "device_name": device.name,
                "token": device.token,
                "server_url": "http://localhost:8000",  # Will be discovered automatically
                "registered_at": device.registered_at.isoformat() if device.registered_at else None,
                "settings": {
                    "auto_discovery": True,
                    "heartbeat_interval": 60,
                    "upload_quality": "high",
                    "timeout": 30
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting device config: {e}")
            return None
    
    @staticmethod
    def deactivate_device(db: Session, device_id: str) -> bool:
        """Deactivate a device (for testing cleanup)"""
        try:
            device = db.query(Device).filter(Device.device_id == device_id).first()
            if device:
                device.is_active = False
                device.network_status = "offline"
                device.last_seen = datetime.datetime.utcnow()
                db.commit()
                
                logger.info(f"🔌 Deactivated device: {device_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deactivating device: {e}")
            return False
    
    @staticmethod
    def cleanup_test_devices(db: Session, prefix: str = "KIOSK_TEST") -> int:
        """Clean up test devices for fresh testing"""
        try:
            test_devices = db.query(Device).filter(
                Device.device_id.like(f"{prefix}%")
            ).all()
            
            count = len(test_devices)
            for device in test_devices:
                db.delete(device)
            
            db.commit()
            logger.info(f"🧹 Cleaned up {count} test devices")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up test devices: {e}")
            return 0

# Global service instance
device_setup_service = DeviceSetupService()
