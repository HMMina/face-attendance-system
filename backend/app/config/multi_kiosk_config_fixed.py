"""
Multi-Kiosk Configuration and Optimization Settings
Cấu hình tối ưu cho hệ thống nhiều kiosk devices
"""
import os
from typing import Dict, Any

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings, Field

class MultiKioskSettings(BaseSettings):
    """Settings optimized for multiple kiosk devices"""
    
    # === CONCURRENCY SETTINGS ===
    MAX_CONCURRENT_RECOGNITIONS: int = Field(default=5, env="MAX_CONCURRENT_RECOGNITIONS")
    WORKER_THREADS: int = Field(default=4, env="WORKER_THREADS")
    RECOGNITION_QUEUE_SIZE: int = Field(default=50, env="RECOGNITION_QUEUE_SIZE")
    
    # === DATABASE OPTIMIZATION ===
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")  # Increased for multiple kiosks
    DB_MAX_OVERFLOW: int = Field(default=40, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=300, env="DB_POOL_RECYCLE")  # 5 minutes
    
    # === DEVICE MANAGEMENT ===
    DEVICE_TIMEOUT_SECONDS: int = Field(default=300, env="DEVICE_TIMEOUT_SECONDS")  # 5 minutes inactive
    MAX_DEVICES_PER_LOCATION: int = Field(default=10, env="MAX_DEVICES_PER_LOCATION")
    DEVICE_HEARTBEAT_INTERVAL: int = Field(default=60, env="DEVICE_HEARTBEAT_INTERVAL")  # 1 minute
    
    # === NETWORK OPTIMIZATION ===
    DISCOVERY_CACHE_TTL: int = Field(default=3600, env="DISCOVERY_CACHE_TTL")  # 1 hour
    SERVER_PING_INTERVAL: int = Field(default=30, env="SERVER_PING_INTERVAL")  # 30 seconds
    CONNECTION_TIMEOUT: int = Field(default=30, env="CONNECTION_TIMEOUT")
    
    # === FILE HANDLING ===
    UPLOAD_SUBFOLDER_BY_DEVICE: bool = Field(default=True, env="UPLOAD_SUBFOLDER_BY_DEVICE")
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    CLEANUP_OLD_FILES_DAYS: int = Field(default=30, env="CLEANUP_OLD_FILES_DAYS")
    
    # === AI SERVICE OPTIMIZATION ===
    AI_SERVICE_POOL_SIZE: int = Field(default=3, env="AI_SERVICE_POOL_SIZE")
    RECOGNITION_TIMEOUT_SECONDS: int = Field(default=15, env="RECOGNITION_TIMEOUT_SECONDS")
    TEMPLATE_CACHE_SIZE: int = Field(default=1000, env="TEMPLATE_CACHE_SIZE")
    
    # === MONITORING ===
    ENABLE_DEVICE_MONITORING: bool = Field(default=True, env="ENABLE_DEVICE_MONITORING")
    LOG_RECOGNITION_STATS: bool = Field(default=True, env="LOG_RECOGNITION_STATS")
    PERFORMANCE_METRICS_ENABLED: bool = Field(default=True, env="PERFORMANCE_METRICS_ENABLED")
    
    class Config:
        env_file = ".env.multi-kiosk"
        env_file_encoding = "utf-8"

# Global instance
multi_kiosk_settings = MultiKioskSettings()

def get_device_upload_path(device_id: str, base_path: str = "./data/uploads") -> str:
    """Get device-specific upload path to avoid conflicts"""
    if multi_kiosk_settings.UPLOAD_SUBFOLDER_BY_DEVICE:
        return os.path.join(base_path, f"device_{device_id}")
    return base_path

def get_optimized_db_config() -> Dict[str, Any]:
    """Get database configuration optimized for multiple kiosks"""
    return {
        "pool_size": multi_kiosk_settings.DB_POOL_SIZE,
        "max_overflow": multi_kiosk_settings.DB_MAX_OVERFLOW,
        "pool_timeout": multi_kiosk_settings.DB_POOL_TIMEOUT,
        "pool_recycle": multi_kiosk_settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
        "echo": False,  # Disable SQL logging in production for performance
    }

def validate_device_capacity(active_devices: int) -> bool:
    """Validate if system can handle additional devices"""
    max_capacity = multi_kiosk_settings.MAX_DEVICES_PER_LOCATION
    return active_devices < max_capacity
