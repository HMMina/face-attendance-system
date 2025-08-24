"""
System Monitoring API for Multi-Kiosk Environment
API giám sát hệ thống nhiều kiosk devices
"""
from fastapi import APIRouter, Depends, HTTPException
from app.services.device_manager import get_device_manager, DeviceManager
from app.config.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import psutil
import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/devices")
async def get_devices_status(device_manager: DeviceManager = Depends(get_device_manager)):
    """Get status of all registered devices"""
    try:
        stats = device_manager.get_system_stats()
        return {
            "success": True,
            "timestamp": datetime.datetime.now().isoformat(),
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting device status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system")
async def get_system_metrics(
    db: Session = Depends(get_db),
    device_manager: DeviceManager = Depends(get_device_manager)
):
    """Get overall system performance metrics"""
    try:
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database metrics
        db_pool_status = _get_db_pool_metrics()
        
        # Device metrics
        device_stats = device_manager.get_system_stats()
        
        # Attendance stats (last 24 hours)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        attendance_count = db.execute(
            text("SELECT COUNT(*) FROM attendance WHERE timestamp >= :yesterday"),
            {"yesterday": yesterday}
        ).scalar()
        
        return {
            "success": True,
            "timestamp": datetime.datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "used": memory.used,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "percent": (disk.used / disk.total) * 100
                }
            },
            "database": db_pool_status,
            "devices": device_stats,
            "attendance": {
                "last_24h": attendance_count
            }
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check_detailed(
    db: Session = Depends(get_db),
    device_manager: DeviceManager = Depends(get_device_manager)
):
    """Detailed health check for load balancer"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False
    
    # Get device count
    active_devices = device_manager.get_device_count()
    
    # Check system resources
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    # Determine overall health
    is_healthy = (
        db_healthy and 
        cpu_percent < 90 and 
        memory_percent < 90 and
        active_devices < 50  # Arbitrary limit
    )
    
    status_code = 200 if is_healthy else 503
    
    health_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.datetime.now().isostring(),
        "checks": {
            "database": "ok" if db_healthy else "error",
            "cpu": f"{cpu_percent}%",
            "memory": f"{memory_percent}%",
            "active_devices": active_devices
        }
    }
    
    if not is_healthy:
        raise HTTPException(status_code=status_code, detail=health_data)
    
    return health_data

@router.post("/devices/{device_id}/heartbeat")
async def device_heartbeat(
    device_id: str,
    device_manager: DeviceManager = Depends(get_device_manager)
):
    """Device heartbeat endpoint"""
    try:
        success = await device_manager.register_device(device_id)
        return {
            "success": success,
            "device_id": device_id,
            "timestamp": datetime.datetime.now().isostring()
        }
    except Exception as e:
        logger.error(f"Heartbeat error for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics(device_manager: DeviceManager = Depends(get_device_manager)):
    """Get performance metrics for monitoring dashboard"""
    try:
        device_stats = device_manager.get_system_stats()
        
        return {
            "success": True,
            "timestamp": datetime.datetime.now().isostring(),
            "metrics": {
                "total_devices": device_stats["total_devices"],
                "active_devices": device_stats["active_devices"],
                "avg_response_time": device_stats["avg_response_time"],
                "total_requests": device_stats["total_requests"],
                "requests_per_minute": _calculate_rpm(device_stats),
                "system_load": {
                    "cpu": psutil.cpu_percent(),
                    "memory": psutil.virtual_memory().percent,
                    "active_connections": _get_active_connections()
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_db_pool_metrics() -> Dict[str, Any]:
    """Get database connection pool metrics"""
    try:
        from app.config.database import engine
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    except Exception as e:
        logger.error(f"Failed to get DB pool metrics: {e}")
        return {"error": str(e)}

def _calculate_rpm(device_stats: Dict) -> float:
    """Calculate requests per minute across all devices"""
    try:
        total_requests = device_stats.get("total_requests", 0)
        active_devices = device_stats.get("active_devices", 1)
        
        # Rough estimate based on device count and avg response time
        if active_devices > 0:
            avg_response_time = device_stats.get("avg_response_time", 1.0)
            estimated_rpm = (60 / max(avg_response_time, 0.1)) * active_devices
            return round(estimated_rpm, 2)
        
        return 0.0
    except Exception:
        return 0.0

def _get_active_connections() -> int:
    """Get number of active network connections"""
    try:
        connections = psutil.net_connections(kind='tcp')
        return len([c for c in connections if c.status == 'ESTABLISHED'])
    except Exception:
        return 0
