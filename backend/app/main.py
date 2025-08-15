"""
FastAPI entry point for Face Attendance System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import employees, devices, attendance, auth, network, recognition, discovery
from app.config.database import test_connection
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Face Attendance System Backend")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    return {
        "status": "healthy",
        "database": "connected" if db_status else "disconnected",
        "service": "face-attendance-backend"
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

@app.get("/")
def root():
    return {"msg": "Face Attendance System Backend is running"}

@app.get("/test")
def test_endpoint():
    return {"test": "API working", "employees_count": 2}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
