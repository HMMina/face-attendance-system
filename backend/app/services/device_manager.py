"""
Device Management Service for Multi-Kiosk Environment
Quản lý nhiều thiết bị kiosk trong cùng hệ thống
"""
import asyncio
import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

@dataclass
class DeviceStatus:
    """Device status information"""
    device_id: str
    device_name: str
    ip_address: Optional[str]
    last_seen: datetime.datetime
    is_active: bool
    requests_count: int
    avg_response_time: float
    location: Optional[str] = None
    
class DeviceManager:
    """Manages multiple kiosk devices"""
    
    def __init__(self):
        self._active_devices: Dict[str, DeviceStatus] = {}
        self._device_locks: Dict[str, asyncio.Lock] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stats_lock = asyncio.Lock()
        
    async def register_device(self, device_id: str, device_name: str = "", 
                            ip_address: str = "", location: str = "") -> bool:
        """Register a new device or update existing device"""
        try:
            async with self._stats_lock:
                now = datetime.datetime.now()
                
                if device_id in self._active_devices:
                    # Update existing device
                    device = self._active_devices[device_id]
                    device.last_seen = now
                    device.is_active = True
                    if ip_address:
                        device.ip_address = ip_address
                    if device_name:
                        device.device_name = device_name
                    if location:
                        device.location = location
                else:
                    # Register new device
                    self._active_devices[device_id] = DeviceStatus(
                        device_id=device_id,
                        device_name=device_name or f"Kiosk_{device_id}",
                        ip_address=ip_address,
                        last_seen=now,
                        is_active=True,
                        requests_count=0,
                        avg_response_time=0.0,
                        location=location
                    )
                    self._device_locks[device_id] = asyncio.Lock()
                    
                logger.info(f"📱 Device registered: {device_id} from {ip_address}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register device {device_id}: {e}")
            return False
    
    async def update_device_stats(self, device_id: str, response_time: float):
        """Update device statistics"""
        async with self._stats_lock:
            if device_id in self._active_devices:
                device = self._active_devices[device_id]
                device.requests_count += 1
                device.last_seen = datetime.datetime.now()
                
                # Calculate rolling average response time
                current_avg = device.avg_response_time
                count = device.requests_count
                device.avg_response_time = ((current_avg * (count - 1)) + response_time) / count
    
    async def get_device_lock(self, device_id: str) -> asyncio.Lock:
        """Get device-specific lock for concurrent operations"""
        if device_id not in self._device_locks:
            async with self._stats_lock:
                if device_id not in self._device_locks:
                    self._device_locks[device_id] = asyncio.Lock()
        return self._device_locks[device_id]
    
    def get_active_devices(self) -> List[DeviceStatus]:
        """Get list of all active devices"""
        return [device for device in self._active_devices.values() if device.is_active]
    
    def get_device_count(self) -> int:
        """Get count of active devices"""
        return len([d for d in self._active_devices.values() if d.is_active])
    
    async def cleanup_inactive_devices(self, timeout_minutes: int = 5):
        """Remove devices that haven't been seen for timeout_minutes"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=timeout_minutes)
        
        async with self._stats_lock:
            inactive_devices = []
            for device_id, device in self._active_devices.items():
                if device.last_seen < cutoff_time:
                    device.is_active = False
                    inactive_devices.append(device_id)
            
            if inactive_devices:
                logger.info(f"🔌 Marked {len(inactive_devices)} devices as inactive: {inactive_devices}")
    
    async def start_cleanup_task(self, interval_minutes: int = 1):
        """Start background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            return
            
        async def cleanup_worker():
            while True:
                try:
                    await self.cleanup_inactive_devices()
                    await asyncio.sleep(interval_minutes * 60)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute on error
        
        self._cleanup_task = asyncio.create_task(cleanup_worker())
        logger.info(f"🧹 Started device cleanup task (interval: {interval_minutes}min)")
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Stopped device cleanup task")
    
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        active_devices = self.get_active_devices()
        
        if not active_devices:
            return {
                "total_devices": 0,
                "active_devices": 0,
                "avg_response_time": 0.0,
                "total_requests": 0
            }
        
        total_requests = sum(d.requests_count for d in active_devices)
        avg_response_time = sum(d.avg_response_time for d in active_devices) / len(active_devices)
        
        return {
            "total_devices": len(self._active_devices),
            "active_devices": len(active_devices),
            "avg_response_time": round(avg_response_time, 3),
            "total_requests": total_requests,
            "devices": [
                {
                    "device_id": d.device_id,
                    "device_name": d.device_name,
                    "ip_address": d.ip_address,
                    "last_seen": d.last_seen.isoformat(),
                    "requests_count": d.requests_count,
                    "avg_response_time": round(d.avg_response_time, 3),
                    "location": d.location
                }
                for d in active_devices
            ]
        }

# Global device manager instance
device_manager = DeviceManager()

async def get_device_manager() -> DeviceManager:
    """Dependency for getting device manager"""
    return device_manager
