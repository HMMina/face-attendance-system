"""
Optimized FastAPI application with clean architecture
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
import sys

# Import core modules
from app.core.config import settings
from app.core.exceptions import FaceAttendanceException
from app.db.session import init_db, close_db_connections, check_db_connection

# Import API routers
from app.api.v1 import (
    employees,
    devices,
    attendance,
    auth,
    network,
    recognition,
    discovery
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        *([logging.FileHandler(settings.LOG_FILE)] if settings.LOG_FILE else [])
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
        
        # Check database connection
        if check_db_connection():
            logger.info("✅ Database connection verified")
        else:
            logger.error("❌ Database connection failed")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Log server info
    logger.info(f"🌐 Server running on {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    logger.info(f"📚 API documentation available at /docs")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Face Attendance System")
    close_db_connections()
    logger.info("✅ Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Face Recognition Attendance System with clean architecture",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add security middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", settings.SERVER_HOST]
    )

# Add CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Request-ID"]
    )


# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log requests and add timing"""
    start_time = time.time()
    
    # Generate request ID for tracking
    request_id = f"{int(start_time * 1000000)}"
    
    # Log request
    logger.info(
        f"🔄 [{request_id}] {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    response.headers["X-Request-ID"] = request_id
    
    # Log response
    status_emoji = "✅" if response.status_code < 400 else "❌"
    logger.info(
        f"{status_emoji} [{request_id}] {response.status_code} "
        f"in {process_time:.3f}s"
    )
    
    return response


# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    
    return response


# Include API routers
app.include_router(
    employees.router,
    prefix=f"{settings.API_V1_STR}/employees",
    tags=["employees"]
)
app.include_router(
    devices.router,
    prefix=f"{settings.API_V1_STR}/devices",
    tags=["devices"]
)
app.include_router(
    attendance.router,
    prefix=f"{settings.API_V1_STR}/attendance",
    tags=["attendance"]
)
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)
app.include_router(
    network.router,
    prefix=f"{settings.API_V1_STR}/network",
    tags=["network"]
)
app.include_router(
    recognition.router,
    prefix=f"{settings.API_V1_STR}/recognition",
    tags=["recognition"]
)
app.include_router(
    discovery.router,
    prefix=f"{settings.API_V1_STR}/discovery",
    tags=["discovery"]
)


# Root endpoints
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with system information"""
    return {
        "message": f"🎯 {settings.PROJECT_NAME} API",
        "version": settings.PROJECT_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else None
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "timestamp": int(time.time())
    }


@app.get("/metrics", tags=["metrics"])
async def get_metrics():
    """Basic metrics endpoint"""
    if not settings.ENABLE_METRICS:
        return {"error": "Metrics disabled"}
    
    return {
        "uptime": int(time.time()),
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return Response(
        content=f'{{"error": "{exc.detail}", "status_code": {exc.status_code}}}',
        status_code=exc.status_code,
        headers={"Content-Type": "application/json"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return Response(
        content=f'{{"error": "Validation failed", "details": {exc.errors()}}}',
        status_code=422,
        headers={"Content-Type": "application/json"}
    )


@app.exception_handler(FaceAttendanceException)
async def face_attendance_exception_handler(request: Request, exc: FaceAttendanceException):
    """Handle custom application exceptions"""
    logger.error(f"Application error: {exc.message}")
    return Response(
        content=f'{{"error": "{exc.message}", "code": "{exc.code}"}}',
        status_code=400,
        headers={"Content-Type": "application/json"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    error_message = str(exc) if settings.DEBUG else "Internal server error"
    
    return Response(
        content=f'{{"error": "{error_message}"}}',
        status_code=500,
        headers={"Content-Type": "application/json"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG,
        access_log=settings.DEBUG
    )
