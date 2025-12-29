"""
Structured logging setup with correlation IDs.

Provides JSON-formatted logging with request correlation for debugging and monitoring.
"""
import logging
import sys
import uuid
from datetime import datetime
from typing import Optional
from contextvars import ContextVar

from src.config.settings import get_settings

# Context variable to store correlation ID for the current request
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter that adds correlation ID to log records.

    Correlation IDs help trace requests through the system.
    """

    def filter(self, record):
        correlation_id = correlation_id_var.get()
        record.correlation_id = correlation_id if correlation_id else "N/A"
        return True


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs log records as JSON for easier parsing by log aggregation tools.
    """

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": getattr(record, 'correlation_id', 'N/A'),
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # Format as JSON string
        import json
        return json.dumps(log_data)


def setup_logging():
    """
    Configure structured logging for the application.

    Sets up:
    - JSON formatting for production
    - Correlation ID tracking
    - Appropriate log level from settings
    """
    settings = get_settings()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Use JSON formatter for production, simple formatter for development
    if settings.environment == "production":
        handler.setFormatter(JSONFormatter())
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
        )
        handler.setFormatter(formatter)

    # Add correlation ID filter
    handler.addFilter(CorrelationIdFilter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    root_logger.addHandler(handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger


def set_correlation_id(correlation_id: Optional[str] = None):
    """
    Set correlation ID for the current context.

    Args:
        correlation_id: Correlation ID string, or None to generate a new one
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """
    Get the correlation ID for the current context.

    Returns:
        Correlation ID string or None if not set
    """
    return correlation_id_var.get()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
