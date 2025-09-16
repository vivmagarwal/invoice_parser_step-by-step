"""
Custom Exception Classes and Error Handling

Provides centralized exception handling with standardized error responses.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

from app.models.api_responses import ErrorResponse, ValidationErrorResponse, ErrorCodes

logger = logging.getLogger(__name__)


# Custom Exception Classes

class BaseAppException(Exception):
    """Base exception class for application-specific errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseAppException):
    """Exception for validation errors."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, list]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )
        self.field_errors = field_errors or {}


class AuthenticationException(BaseAppException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code=ErrorCodes.AUTHENTICATION_REQUIRED,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(BaseAppException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code=ErrorCodes.AUTHORIZATION_FAILED,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ResourceNotFoundException(BaseAppException):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", resource_type: str = None):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(
            message=message,
            error_code=ErrorCodes.RESOURCE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ResourceAlreadyExistsException(BaseAppException):
    """Exception for resource already exists errors."""
    
    def __init__(self, message: str = "Resource already exists", resource_type: str = None):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(
            message=message,
            error_code=ErrorCodes.RESOURCE_ALREADY_EXISTS,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class ProcessingException(BaseAppException):
    """Exception for processing errors."""
    
    def __init__(self, message: str = "Processing failed", processing_type: str = None):
        details = {"processing_type": processing_type} if processing_type else {}
        super().__init__(
            message=message,
            error_code=ErrorCodes.PROCESSING_FAILED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class FileException(BaseAppException):
    """Exception for file-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = ErrorCodes.INVALID_REQUEST,
        file_name: str = None,
        file_size: int = None
    ):
        details = {}
        if file_name:
            details["file_name"] = file_name
        if file_size:
            details["file_size"] = file_size
            
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class FileTooLargeException(FileException):
    """Exception for file size limit exceeded."""
    
    def __init__(self, file_size: int, max_size: int, file_name: str = None):
        super().__init__(
            message=f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            error_code=ErrorCodes.FILE_TOO_LARGE,
            file_name=file_name,
            file_size=file_size
        )
        self.details.update({"max_size": max_size})


class UnsupportedFileTypeException(FileException):
    """Exception for unsupported file types."""
    
    def __init__(self, file_type: str, supported_types: list = None, file_name: str = None):
        message = f"Unsupported file type: {file_type}"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
            
        super().__init__(
            message=message,
            error_code=ErrorCodes.UNSUPPORTED_FILE_TYPE,
            file_name=file_name
        )
        self.details.update({
            "file_type": file_type,
            "supported_types": supported_types or []
        })


class DatabaseException(BaseAppException):
    """Exception for database errors."""
    
    def __init__(self, message: str = "Database operation failed", operation: str = None):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            error_code=ErrorCodes.DATABASE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceException(BaseAppException):
    """Exception for external service errors."""
    
    def __init__(self, message: str = "External service error", service_name: str = None):
        details = {"service_name": service_name} if service_name else {}
        super().__init__(
            message=message,
            error_code=ErrorCodes.EXTERNAL_SERVICE_ERROR,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


# Exception Handlers

async def base_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.warning(f"Application exception: {exc.message} (Code: {exc.error_code})")
    
    if isinstance(exc, ValidationException):
        response = ValidationErrorResponse.create(
            message=exc.message,
            field_errors=exc.field_errors
        )
    else:
        response = ErrorResponse.create(
            message=exc.message,
            error_code=exc.error_code,
            error_details=exc.details
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.detail} (Status: {exc.status_code})")
    
    # Map common HTTP status codes to error codes
    error_code_map = {
        400: ErrorCodes.INVALID_REQUEST,
        401: ErrorCodes.AUTHENTICATION_REQUIRED,
        403: ErrorCodes.AUTHORIZATION_FAILED,
        404: ErrorCodes.RESOURCE_NOT_FOUND,
        409: ErrorCodes.RESOURCE_ALREADY_EXISTS,
        422: ErrorCodes.VALIDATION_ERROR,
        429: ErrorCodes.RATE_LIMIT_EXCEEDED,
        500: ErrorCodes.INTERNAL_SERVER_ERROR,
        503: ErrorCodes.SERVICE_UNAVAILABLE,
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCodes.INTERNAL_SERVER_ERROR)
    
    response = ErrorResponse.create(
        message=exc.detail,
        error_code=error_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Convert Pydantic errors to field errors
    field_errors = {}
    for error in exc.errors():
        field_name = ".".join(str(loc) for loc in error["loc"])
        error_msg = error["msg"]
        
        if field_name not in field_errors:
            field_errors[field_name] = []
        field_errors[field_name].append(error_msg)
    
    response = ValidationErrorResponse.create(
        message="Request validation failed",
        field_errors=field_errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected exception: {str(exc)}", exc_info=True)
    
    response = ErrorResponse.create(
        message="An unexpected error occurred",
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        error_details={"exception_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.dict()
    )


# Utility functions

def handle_database_error(operation: str):
    """Decorator to handle database errors."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Database error in {operation}: {str(e)}")
                raise DatabaseException(f"Database {operation} failed", operation=operation)
        return wrapper
    return decorator


def handle_processing_error(processing_type: str):
    """Decorator to handle processing errors."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            except BaseAppException:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                logger.error(f"Processing error in {processing_type}: {str(e)}")
                raise ProcessingException(f"{processing_type} failed", processing_type=processing_type)
        return wrapper
    return decorator


# Import asyncio for decorator functions
import asyncio


# Export all exception classes and handlers
__all__ = [
    # Exception classes
    "BaseAppException",
    "ValidationException", 
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ResourceAlreadyExistsException",
    "ProcessingException",
    "FileException",
    "FileTooLargeException",
    "UnsupportedFileTypeException",
    "DatabaseException",
    "ExternalServiceException",
    
    # Exception handlers
    "base_app_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "general_exception_handler",
    
    # Utility decorators
    "handle_database_error",
    "handle_processing_error"
]
