"""
Production-grade middleware
"""
import time
import uuid
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import traceback

from app.core.exceptions import TradingPlatformException
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests"""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration * 1000,
                }
            )
            
            # Add performance header
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": duration * 1000,
                },
                exc_info=True
            )
            
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Handle exceptions and return proper error responses"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except TradingPlatformException as e:
            logger.error(
                f"TradingPlatformException: {e.message}",
                extra={
                    "error_type": type(e).__name__,
                    "status_code": e.status_code,
                    "details": e.details,
                }
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "message": e.message,
                        "type": type(e).__name__,
                        "details": e.details,
                    }
                }
            )
            
        except Exception as e:
            logger.error(
                f"Unhandled exception: {str(e)}",
                extra={
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc(),
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "message": "Internal server error",
                        "type": "InternalServerError",
                    }
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self.request_counts = {
            ip: count_time
            for ip, count_time in self.request_counts.items()
            if current_time - count_time["timestamp"] < 60
        }
        
        # Check rate limit
        if client_ip in self.request_counts:
            count_data = self.request_counts[client_ip]
            if count_data["count"] >= self.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for {client_ip}",
                    extra={"client_ip": client_ip, "path": request.url.path}
                )
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "message": "Rate limit exceeded",
                            "type": "RateLimitError",
                        }
                    },
                    headers={"Retry-After": "60"}
                )
            
            count_data["count"] += 1
        else:
            self.request_counts[client_ip] = {
                "count": 1,
                "timestamp": current_time
            }
        
        response = await call_next(request)
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware with production settings"""
    
    def __init__(self, app: ASGIApp, allowed_origins: list):
        super().__init__(app)
        self.allowed_origins = allowed_origins
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        if origin and origin in self.allowed_origins:
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        
        response = await call_next(request)
        return response
