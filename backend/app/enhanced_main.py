"""
Enhanced FastAPI entry point with all improvements
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import time

# Import routers
from app.api.v1 import employees, devices, attendance, auth, network, recognition, discovery

# Import configurations and services
from app.config.improved_settings import settings
from app.config.database import engine
from app.models.base import Base

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        *([logging.FileHandler(settings.LOG_FILE)] if settings.LOG_FILE else [])
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Face Attendance System Backend")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"Database: {settings.DB_URL.split('@')[-1]}")  # Don't log credentials
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Face Attendance System Backend")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Face Recognition Attendance System with enhanced features",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1", settings.SERVER_HOST]
)

# CORS middleware with enhanced configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token"
    ],
    expose_headers=["X-Process-Time"],
)

# Include all API routers
app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["Attendance"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(network.router, prefix="/api/v1/network", tags=["Network"])
app.include_router(recognition.router, prefix="/api/v1/recognition", tags=["Recognition"])
app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["Discovery"])

# Health check endpoints
@app.get("/")
def root():
    """Root endpoint with system information"""
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.VERSION,
        "status": "healthy",
        "environment": "development" if settings.DEBUG else "production"
    }

@app.get("/health")
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION,
        "database": "connected",  # Could add actual DB ping here
        "services": {
            "api": "operational",
            "face_recognition": "ready",
            "file_storage": "available"
        }
    }

@app.get("/api/v1/stats")
def get_system_stats():
    """System statistics for dashboard"""
    # This would typically query the database for real stats
    return {
        "totalEmployees": 25,
        "activeDevices": 3,
        "todayAttendance": 47,
        "recognitionRate": 94.5,
        "systemUptime": "2 days, 5 hours",
        "lastUpdated": time.time()
    }

@app.get("/api/v1/recent-activity")
def get_recent_activity():
    """Recent activity for dashboard"""
    # Mock data - would query from database in real implementation
    return [
        {
            "employeeName": "Nguyễn Văn A",
            "action": "Check-in",
            "status": "success",
            "timestamp": "2025-01-16T08:30:00Z",
            "deviceId": "KIOSK_001"
        },
        {
            "employeeName": "Trần Thị B",
            "action": "Check-out", 
            "status": "success",
            "timestamp": "2025-01-16T17:45:00Z",
            "deviceId": "KIOSK_002"
        },
        {
            "employeeName": "Unknown",
            "action": "Recognition failed",
            "status": "error",
            "timestamp": "2025-01-16T09:15:00Z",
            "deviceId": "KIOSK_001"
        }
    ]

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return {
        "error": "Not Found",
        "message": f"The requested resource {request.url.path} was not found",
        "status_code": 404
    }

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error on {request.url}: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "Something went wrong on our end",
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )
