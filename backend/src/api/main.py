"""
FastAPI application entry point.

Configures the FastAPI app with:
- CORS middleware for frontend communication
- Logging middleware for request tracking
- Error handlers for graceful error responses
- Health check endpoint
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.config.settings import get_settings
from src.utils.app_logging import setup_logging, set_correlation_id, get_logger
from src.models.schemas import ErrorResponse

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
    - Log application start
    - Initialize settings
    - Initialize database

    Shutdown:
    - Log application shutdown
    """
    # Startup
    settings = get_settings()
    logger.info(
        f"Starting FastAPI application in {settings.environment} environment",
        extra={"extra_fields": {"environment": settings.environment}}
    )

    # Initialize database
    from src.utils.database import init_database, create_tables
    try:
        init_database()
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        # Continue anyway - will fail on first request if database is required

    yield
    # Shutdown
    logger.info("Shutting down FastAPI application")


# Create FastAPI app
app = FastAPI(
    title="Physical AI & Humanoid Robotics Textbook API",
    description="Backend API for the interactive textbook platform with RAG-powered chatbot",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ==================== Middleware ====================

# CORS Middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware to log all HTTP requests with correlation IDs.

    Adds:
    - Correlation ID for request tracing
    - Request logging (method, path, client)
    - Response logging (status code, latency)
    """
    import time

    # Set correlation ID
    correlation_id = request.headers.get("X-Correlation-ID")
    set_correlation_id(correlation_id)

    # Log request
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "extra_fields": {
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        }
    )

    # Process request
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time

    # Log response
    logger.info(
        f"Response {response.status_code}",
        extra={
            "extra_fields": {
                "status_code": response.status_code,
                "latency_ms": round(latency * 1000, 2)
            }
        }
    )

    # Add correlation ID to response headers
    from src.utils.app_logging import get_correlation_id
    response.headers["X-Correlation-ID"] = get_correlation_id() or "N/A"

    return response


# ==================== Error Handlers ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors (400 Bad Request).

    Returns structured error response with field-level details.
    """
    logger.warning(
        f"Validation error: {exc}",
        extra={"extra_fields": {"errors": exc.errors()}}
    )

    # Extract first error for user-friendly message
    first_error = exc.errors()[0] if exc.errors() else {}
    field = first_error.get("loc", ["unknown"])[-1]
    error_type = first_error.get("type", "validation_error")

    error_response = ErrorResponse(
        error="ValidationError",
        message=f"Invalid value for field '{field}': {first_error.get('msg', 'validation failed')}",
        details={
            "field": field,
            "constraint": error_type,
            "all_errors": exc.errors()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors (500 Internal Server Error).

    Logs full exception and returns sanitized error to client.
    """
    from src.utils.app_logging import get_correlation_id

    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "extra_fields": {
                "exception_type": type(exc).__name__,
                "path": request.url.path
            }
        }
    )

    error_response = ErrorResponse(
        error="InternalServerError",
        message="An unexpected error occurred. Please try again later.",
        details={
            "request_id": get_correlation_id()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


# ==================== Routes ====================

@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": "Physical AI & Humanoid Robotics Textbook API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# Import and include routers
from src.api.chat import router as chat_router
from src.api.health import router as health_router

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True if settings.environment == "development" else False,
        log_level=settings.log_level.lower()
    )
