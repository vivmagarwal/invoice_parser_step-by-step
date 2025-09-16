"""
Structured Logging Configuration

Provides comprehensive logging with structured output, performance metrics,
and request tracking for production monitoring.
"""
import json
import logging
import logging.config
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
from functools import wraps

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context if available
        request_id = request_id_var.get('')
        if request_id:
            log_entry["request_id"] = request_id
        
        user_id = user_id_var.get('')
        if user_id:
            log_entry["user_id"] = user_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }
        
        # Add extra fields from log record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with performance metrics."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response with timing information."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract user ID from authorization header if present
        auth_header = request.headers.get('authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                from app.core.security import verify_token
                token = auth_header.split(' ')[1]
                payload = verify_token(token)
                if payload:
                    user_id_var.set(payload.get('sub', ''))
            except Exception:
                pass  # Continue without user ID if token verification fails
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger = logging.getLogger("app.requests")
        logger.info(
            "Request started",
            extra={
                "request_method": request.method,
                "request_url": str(request.url),
                "request_path": request.url.path,
                "request_query": str(request.url.query) if request.url.query else None,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get('user-agent'),
                "content_type": request.headers.get('content-type'),
                "content_length": request.headers.get('content-length'),
                "request_id": request_id
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "response_status": response.status_code,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "response_size": response.headers.get('content-length'),
                    "request_id": request_id
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Log error
            logger.error(
                "Request failed",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "request_id": request_id
                },
                exc_info=True
            )
            
            raise


class PerformanceLogger:
    """Logger for performance metrics and monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger("app.performance")
    
    def log_database_query(self, query_type: str, duration: float, table: str = None):
        """Log database query performance."""
        self.logger.info(
            "Database query executed",
            extra={
                "query_type": query_type,
                "duration_ms": round(duration * 1000, 2),
                "table": table,
                "metric_type": "database_query"
            }
        )
    
    def log_ai_processing(self, operation: str, duration: float, tokens: int = None):
        """Log AI processing performance."""
        self.logger.info(
            "AI processing completed",
            extra={
                "operation": operation,
                "duration_ms": round(duration * 1000, 2),
                "tokens": tokens,
                "metric_type": "ai_processing"
            }
        )
    
    def log_file_operation(self, operation: str, duration: float, file_size: int = None):
        """Log file operation performance."""
        self.logger.info(
            "File operation completed",
            extra={
                "operation": operation,
                "duration_ms": round(duration * 1000, 2),
                "file_size_bytes": file_size,
                "metric_type": "file_operation"
            }
        )


def performance_monitor(operation_type: str, operation_name: str = None):
    """Decorator to monitor function performance."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger("app.performance")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"{operation_type} completed",
                    extra={
                        "operation_type": operation_type,
                        "operation_name": operation_name or func.__name__,
                        "duration_ms": round(duration * 1000, 2),
                        "status": "success",
                        "metric_type": "function_performance"
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    f"{operation_type} failed",
                    extra={
                        "operation_type": operation_type,
                        "operation_name": operation_name or func.__name__,
                        "duration_ms": round(duration * 1000, 2),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "metric_type": "function_performance"
                    },
                    exc_info=True
                )
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger("app.performance")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"{operation_type} completed",
                    extra={
                        "operation_type": operation_type,
                        "operation_name": operation_name or func.__name__,
                        "duration_ms": round(duration * 1000, 2),
                        "status": "success",
                        "metric_type": "function_performance"
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    f"{operation_type} failed",
                    extra={
                        "operation_type": operation_type,
                        "operation_name": operation_name or func.__name__,
                        "duration_ms": round(duration * 1000, 2),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "metric_type": "function_performance"
                    },
                    exc_info=True
                )
                
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def setup_logging(environment: str = "development", log_level: str = "INFO") -> Dict[str, Any]:
    """Setup structured logging configuration."""
    
    # Determine if we should use JSON formatting
    use_json = environment in ["production", "staging"]
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "structured" if use_json else "simple",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "structured",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file"] if environment == "production" else ["console"],
                "propagate": False
            },
            "app.requests": {
                "level": "INFO",
                "handlers": ["console", "file"] if environment == "production" else ["console"],
                "propagate": False
            },
            "app.performance": {
                "level": "INFO",
                "handlers": ["console", "file"] if environment == "production" else ["console"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # Reduce SQL noise unless debugging
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    return config


# Create global performance logger instance
performance_logger = PerformanceLogger()

# Export commonly used components
__all__ = [
    "StructuredFormatter",
    "RequestLoggingMiddleware", 
    "PerformanceLogger",
    "performance_monitor",
    "setup_logging",
    "performance_logger",
    "request_id_var",
    "user_id_var"
]
