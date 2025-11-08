"""
Main FastAPI application for Algorithmic Trading Platform
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import init_db, check_db_connection, check_redis_connection
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import (
    TradingPlatformException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    DatabaseError
)
from app.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware
)
from app.api.v1.api import api_router
from app.core.websocket import websocket_router
from app.instrumentation import metrics_router, MetricsMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting application")
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


app = FastAPI(
    title="Algorithmic Trading Platform",
    description="Backtesting and Live Execution Platform for Algorithmic Trading",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add production middleware (order matters!)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(MetricsMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(TradingPlatformException)
async def trading_platform_exception_handler(request: Request, exc: TradingPlatformException):
    """Handle custom trading platform exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": type(exc).__name__,
                "details": exc.details,
            }
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database exceptions"""
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Database error occurred",
                "type": "DatabaseError",
            }
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "message": str(exc),
                "type": "ValidationError",
            }
        }
    )


# Security
security = HTTPBearer()

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/ws")
app.include_router(metrics_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Algorithmic Trading Platform API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Database health check
    if check_db_connection():
        health_status["checks"]["database"] = "healthy"
    else:
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Redis health check
    if check_redis_connection():
        health_status["checks"]["redis"] = "healthy"
    else:
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    if check_db_connection():
        return {"status": "ready"}
    else:
        logger.error("Readiness check failed: database not available")
        return JSONResponse(
            content={"status": "not ready"},
            status_code=503
        )


@app.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {"status": "alive"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
