import logging
import structlog
from app.core.config import settings

def setup_logging():
    """Configure structlog for JSON logging in production and readable logging in dev."""
    
    # Standard library logging configuration
    logging.basicConfig(
        format="%(message)s",
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if not settings.DEBUG:
        # Production: JSON logs
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Pretty colorized console logs
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    return structlog.get_logger(name)
