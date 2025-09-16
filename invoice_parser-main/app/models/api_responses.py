"""
Standardized API Response Models

Provides consistent response structures across all API endpoints.
"""
from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Generic type for data payload
T = TypeVar('T')


class ResponseStatus(str, Enum):
    """Standard response status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(..., description="Current page number", ge=1)
    limit: int = Field(..., description="Items per page", ge=1, le=100)
    total: int = Field(..., description="Total number of items", ge=0)
    pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationMeta":
        """Create pagination metadata from basic parameters."""
        pages = (total + limit - 1) // limit if total > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total=total,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API endpoints."""
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    data: Optional[T] = Field(None, description="Response data payload")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class SuccessResponse(BaseResponse[T]):
    """Success response model."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    
    @classmethod
    def create(cls, data: T = None, message: str = "Operation completed successfully") -> "SuccessResponse[T]":
        """Create a success response."""
        return cls(status=ResponseStatus.SUCCESS, message=message, data=data)


class ErrorResponse(BaseResponse[None]):
    """Error response model."""
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    @classmethod
    def create(
        cls, 
        message: str, 
        error_code: Optional[str] = None, 
        error_details: Optional[Dict[str, Any]] = None
    ) -> "ErrorResponse":
        """Create an error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            error_code=error_code,
            error_details=error_details
        )


class PaginatedResponse(BaseResponse[List[T]]):
    """Paginated response model."""
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    
    @classmethod
    def create(
        cls,
        data: List[T],
        page: int,
        limit: int,
        total: int,
        message: str = "Data retrieved successfully"
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            pagination=PaginationMeta.create(page, limit, total)
        )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field-specific errors."""
    field_errors: Dict[str, List[str]] = Field(default_factory=dict, description="Field-specific validation errors")
    
    @classmethod
    def create(
        cls,
        message: str = "Validation failed",
        field_errors: Dict[str, List[str]] = None
    ) -> "ValidationErrorResponse":
        """Create a validation error response."""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            error_code="VALIDATION_ERROR",
            field_errors=field_errors or {}
        )


# Specific response models for common use cases

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
    components: Dict[str, Any] = Field(default_factory=dict, description="Component status details")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ProcessingResponse(BaseModel):
    """Response model for processing operations."""
    processing_id: str = Field(..., description="Unique processing identifier")
    status: str = Field(..., description="Processing status")
    progress: Optional[float] = Field(None, description="Processing progress (0-100)", ge=0, le=100)
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    result_url: Optional[str] = Field(None, description="URL to retrieve results")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class FileUploadResponse(BaseModel):
    """Response model for file upload operations."""
    file_id: str = Field(..., description="Unique file identifier")
    original_name: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes", gt=0)
    content_type: str = Field(..., description="MIME content type")
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    download_url: Optional[str] = Field(None, description="URL to download the file")
    thumbnail_url: Optional[str] = Field(None, description="URL to file thumbnail")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


# Response factory functions

def success_response(data: Any = None, message: str = "Operation completed successfully") -> Dict[str, Any]:
    """Create a success response dictionary."""
    return SuccessResponse.create(data=data, message=message).dict()


def error_response(
    message: str, 
    error_code: Optional[str] = None, 
    error_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create an error response dictionary."""
    return ErrorResponse.create(
        message=message, 
        error_code=error_code, 
        error_details=error_details
    ).dict()


def validation_error_response(
    message: str = "Validation failed",
    field_errors: Dict[str, List[str]] = None
) -> Dict[str, Any]:
    """Create a validation error response dictionary."""
    return ValidationErrorResponse.create(
        message=message,
        field_errors=field_errors
    ).dict()


def paginated_response(
    data: List[Any],
    page: int,
    limit: int,
    total: int,
    message: str = "Data retrieved successfully"
) -> Dict[str, Any]:
    """Create a paginated response dictionary."""
    return PaginatedResponse.create(
        data=data,
        page=page,
        limit=limit,
        total=total,
        message=message
    ).dict()


# Common error codes
class ErrorCodes:
    """Standard error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


# Export commonly used types
__all__ = [
    "ResponseStatus",
    "PaginationMeta", 
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "ValidationErrorResponse",
    "HealthCheckResponse",
    "ProcessingResponse",
    "FileUploadResponse",
    "success_response",
    "error_response",
    "validation_error_response",
    "paginated_response",
    "ErrorCodes"
]
