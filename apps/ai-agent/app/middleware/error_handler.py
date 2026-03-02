import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler and request logger."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request context to logger
        structlog_logger = logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            structlog_logger.info(
                "request_processed",
                status_code=response.status_code,
                duration_ms=round(process_time * 1000, 2)
            )
            
            # Add correlation ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            structlog_logger.error(
                "request_failed",
                error=str(exc),
                duration_ms=round(process_time * 1000, 2),
                exc_info=True
            )
            
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "request_id": request_id,
                    "detail": str(exc) if settings.DEBUG else "Check logs for details"
                }
            )
