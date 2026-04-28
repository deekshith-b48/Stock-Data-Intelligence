"""
FastAPI application for Stock Data Intelligence Dashboard.

This module sets up the FastAPI application with:
- CORS middleware for cross-origin requests
- Logging configuration with rotating file handler
- Health check endpoint
- Global error handling

Requirements: 6.1, 10.1, 10.2, 10.5, 20.1, 20.2, 20.3, 20.4, 20.5
"""

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from .schemas import HealthResponse, ErrorResponse
from .endpoints import router
from ..models.connection import get_database

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_file = os.getenv('LOG_FILE', 'app.log')

# Create logger
logger = logging.getLogger(__name__)

# Configure rotating file handler (10 MB max, 5 backup files)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5
)
file_handler.setLevel(log_level)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger.info(f"Logging configured: level={log_level}, file={log_file}")

# Create FastAPI application
app = FastAPI(
    title="Stock Data Intelligence Dashboard API",
    description="REST API for accessing stock market data, metrics, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
# Allow all origins for development; restrict in production
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ['*'] else ['*'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

logger.info(f"CORS configured: allowed_origins={allowed_origins}")


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all API requests with endpoint, method, and response time.
    
    Requirements: 20.2
    """
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    end_time = datetime.utcnow()
    response_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"status={response.status_code} time={response_time:.2f}ms"
    )
    
    return response


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors (400 Bad Request).
    
    Requirements: 10.1, 10.4
    """
    errors = exc.errors()
    error_details = {
        "validation_errors": [
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            }
            for error in errors
        ]
    }
    
    logger.warning(
        f"Validation error for {request.method} {request.url.path}: {error_details}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "INVALID_REQUEST",
            "message": "Request validation failed",
            "details": error_details
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle value errors (400 Bad Request).
    
    Requirements: 10.1, 10.4
    """
    logger.warning(
        f"Value error for {request.method} {request.url.path}: {str(exc)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "INVALID_PARAMETER",
            "message": str(exc)
        }
    )


@app.exception_handler(OperationalError)
async def database_error_handler(request: Request, exc: OperationalError):
    """
    Handle database connection errors (500 Internal Server Error).
    
    Requirements: 10.2, 10.4
    """
    logger.error(
        f"Database error for {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "DATABASE_ERROR",
            "message": "Database connection failed. Please try again later."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions (500 Internal Server Error).
    
    Requirements: 10.2, 10.4
    """
    logger.error(
        f"Unhandled exception for {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Check the health status of the API and database connection"
)
async def health_check():
    """
    Health check endpoint to verify service and database status.
    
    Returns:
        HealthResponse: Service health status
        
    Requirements: 6.1
    """
    # Check database connection
    db_status = "connected"
    try:
        db = get_database()
        with db.get_session() as session:
            session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Health check database error: {e}")
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


# Include API endpoints router
app.include_router(router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    Initialize database connection and log startup information.
    """
    logger.info("Starting Stock Data Intelligence Dashboard API")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./stock_dashboard.db')}")
    
    # Initialize database
    try:
        db = get_database()
        logger.info("Database connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    Clean up resources and close database connections.
    """
    logger.info("Shutting down Stock Data Intelligence Dashboard API")
    
    try:
        db = get_database()
        db.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn for development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=log_level.lower()
    )
