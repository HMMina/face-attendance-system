"""
FastAPI entry point for Face Attendance System with Rolling Template System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1 import employees, devices, attendance, auth, network, recognition, discovery, monitoring, device_management
from app.api import templates
from app.config.database import test_connection
from app.services.device_manager import device_manager
import logging
import os
from pathlib import Path
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Face Attendance System Backend - Multi-Kiosk")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Multi-Kiosk Face Attendance System...")
    
    # Start device manager cleanup task
    await device_manager.start_cleanup_task(interval_minutes=1)
    logger.info("✅ Device manager initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Multi-Kiosk Face Attendance System...")
    await device_manager.stop_cleanup_task()
    logger.info("✅ Cleanup completed")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    device_count = device_manager.get_device_count()
    
    return {
        "status": "healthy",
        "database": "connected" if db_status else "disconnected",
        "service": "face-attendance-backend-multi-kiosk",
        "active_devices": device_count,
        "version": "2.0.0-multi-kiosk"
    }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url} from {request.client.host}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# CORS for local network
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Cho phép tất cả trong development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["Attendance"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(network.router, prefix="/api/v1/network", tags=["Network"])
app.include_router(recognition.router, prefix="/api/v1/recognition", tags=["Recognition"])
app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["Discovery"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["System Monitoring"])
app.include_router(device_management.router, prefix="/api/v1/device-management", tags=["Device Management"])

# Include new Template Management API
app.include_router(templates.router, tags=["Template Management"])

# Static files for admin dashboard
admin_dashboard_path = Path(__file__).parent.parent.parent / "admin-dashboard"
if admin_dashboard_path.exists():
    app.mount("/admin", StaticFiles(directory=str(admin_dashboard_path)), name="admin")
    
    @app.get("/admin", include_in_schema=False)
    async def admin_dashboard():
        """Serve admin dashboard"""
        return FileResponse(str(admin_dashboard_path / "index.html"))
    
    @app.get("/admin/", include_in_schema=False)
    async def admin_dashboard_trailing_slash():
        """Serve admin dashboard with trailing slash"""
        return FileResponse(str(admin_dashboard_path / "index.html"))

@app.get("/")
def root():
    return {
        "msg": "Face Attendance System Backend is running",
        "admin_dashboard": "http://localhost:8000/admin",
        "api_docs": "http://localhost:8000/docs"
    }

@app.get("/test")
def test_endpoint():
    return {"test": "API working", "employees_count": 2}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
