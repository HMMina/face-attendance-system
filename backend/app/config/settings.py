"""
Server settings for local development
"""
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Face Attendance System"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration
    # For SQLite (current):
    # DB_URL: str = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    
    # For PostgreSQL:
    DB_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:Minh452004a5@localhost:5432/face_attendance")
    
    # PostgreSQL Connection Details (if needed separately)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "face_attendance")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "Minh452004a5")
    
    # File upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads/")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # mDNS Discovery
    MDNS_SERVICE_NAME: str = "face-attendance-server"
    MDNS_SERVICE_TYPE: str = "_attendance._tcp.local."
    SERVER_PORT: int = int(os.getenv("PORT", "8000"))

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
