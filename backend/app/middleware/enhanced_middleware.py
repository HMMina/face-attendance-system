"""
Enhanced middleware for better error handling, logging, and performance
"""
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
import traceback
import json
from typing import Callable
from app.config.improved_settings import settings

logger = logging.getLogger(__name__)

class EnhancedLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware with request/response logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url} from {request.client.host}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} in {process_time:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            logger.warning(f"HTTP Exception: {e.status_code} - {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "status_code": e.status_code}
            )
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(e) if settings.DEBUG else "Something went wrong"
                }
            )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: requests for ip, requests in self.clients.items()
            if any(req_time > current_time - self.period for req_time in requests)
        }
        
        # Get client's request history
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Filter recent requests
        recent_requests = [
            req_time for req_time in self.clients[client_ip]
            if req_time > current_time - self.period
        ]
        
        # Check rate limit
        if len(recent_requests) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": self.period}
            )
        
        # Add current request
        recent_requests.append(current_time)
        self.clients[client_ip] = recent_requests
        
        return await call_next(request)

class CompressionMiddleware(BaseHTTPMiddleware):
    """Simple response compression for JSON responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Only compress JSON responses
        if (
            response.headers.get("content-type", "").startswith("application/json")
            and "gzip" in request.headers.get("accept-encoding", "")
        ):
            response.headers["Content-Encoding"] = "gzip"
        
        return response
