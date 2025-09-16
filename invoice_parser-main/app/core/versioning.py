"""
API Versioning Support

Provides version management for API endpoints with backward compatibility.
"""
from enum import Enum
from typing import Optional
from fastapi import Request, Header
import re

class APIVersion(str, Enum):
    """Supported API versions."""
    V1 = "v1"
    V2 = "v2"  # Future version placeholder


class VersioningStrategy(str, Enum):
    """API versioning strategies."""
    URL_PATH = "url_path"          # /api/v1/endpoint
    HEADER = "header"              # Accept: application/vnd.api+json;version=1
    QUERY_PARAM = "query_param"    # /api/endpoint?version=v1


class APIVersionManager:
    """Manages API versioning logic."""
    
    CURRENT_VERSION = APIVersion.V1
    SUPPORTED_VERSIONS = [APIVersion.V1]
    DEFAULT_VERSION = APIVersion.V1
    
    @classmethod
    def get_version_from_path(cls, path: str) -> Optional[APIVersion]:
        """Extract version from URL path."""
        # Match /api/v{version}/ pattern
        match = re.match(r'/api/(v\d+)/', path)
        if match:
            version_str = match.group(1)
            try:
                return APIVersion(version_str)
            except ValueError:
                return None
        return None
    
    @classmethod
    def get_version_from_header(cls, accept_header: str) -> Optional[APIVersion]:
        """Extract version from Accept header."""
        # Match application/vnd.api+json;version=1 pattern
        if accept_header:
            match = re.search(r'version=(\d+)', accept_header)
            if match:
                version_num = match.group(1)
                version_str = f"v{version_num}"
                try:
                    return APIVersion(version_str)
                except ValueError:
                    return None
        return None
    
    @classmethod
    def get_version_from_query(cls, version_param: Optional[str]) -> Optional[APIVersion]:
        """Extract version from query parameter."""
        if version_param:
            try:
                return APIVersion(version_param)
            except ValueError:
                return None
        return None
    
    @classmethod
    def resolve_version(
        cls, 
        request: Request, 
        version_header: Optional[str] = None,
        version_query: Optional[str] = None
    ) -> APIVersion:
        """Resolve API version from request using multiple strategies."""
        
        # Strategy 1: URL path (highest priority)
        path_version = cls.get_version_from_path(request.url.path)
        if path_version and path_version in cls.SUPPORTED_VERSIONS:
            return path_version
        
        # Strategy 2: Header
        if version_header:
            header_version = cls.get_version_from_header(version_header)
            if header_version and header_version in cls.SUPPORTED_VERSIONS:
                return header_version
        
        # Strategy 3: Query parameter
        if version_query:
            query_version = cls.get_version_from_query(version_query)
            if query_version and query_version in cls.SUPPORTED_VERSIONS:
                return query_version
        
        # Default to current version
        return cls.DEFAULT_VERSION
    
    @classmethod
    def is_version_supported(cls, version: APIVersion) -> bool:
        """Check if a version is supported."""
        return version in cls.SUPPORTED_VERSIONS
    
    @classmethod
    def get_version_info(cls) -> dict:
        """Get version information."""
        return {
            "current_version": cls.CURRENT_VERSION.value,
            "default_version": cls.DEFAULT_VERSION.value,
            "supported_versions": [v.value for v in cls.SUPPORTED_VERSIONS],
            "versioning_strategies": [
                "URL path: /api/v1/endpoint",
                "Header: Accept: application/vnd.api+json;version=1",
                "Query parameter: ?version=v1"
            ]
        }


def get_api_version(
    request: Request,
    accept: Optional[str] = Header(None),
    version: Optional[str] = None  # Query parameter
) -> APIVersion:
    """Dependency to get API version from request."""
    return APIVersionManager.resolve_version(request, accept, version)


# Version-specific response models
class VersionedResponse:
    """Base class for versioned responses."""
    
    @classmethod
    def get_response_for_version(cls, data: dict, version: APIVersion) -> dict:
        """Get response structure for specific version."""
        if version == APIVersion.V1:
            return cls._get_v1_response(data)
        # Future versions can be added here
        return cls._get_v1_response(data)  # Default to v1
    
    @classmethod
    def _get_v1_response(cls, data: dict) -> dict:
        """Get v1 response structure."""
        return data


# Deprecation warnings
class DeprecationManager:
    """Manages API deprecation warnings."""
    
    DEPRECATED_VERSIONS = []  # No deprecated versions yet
    DEPRECATION_WARNINGS = {}
    
    @classmethod
    def get_deprecation_warning(cls, version: APIVersion) -> Optional[dict]:
        """Get deprecation warning for version."""
        if version in cls.DEPRECATED_VERSIONS:
            return cls.DEPRECATION_WARNINGS.get(version)
        return None
    
    @classmethod
    def add_deprecation_headers(cls, response_headers: dict, version: APIVersion) -> dict:
        """Add deprecation headers to response."""
        warning = cls.get_deprecation_warning(version)
        if warning:
            response_headers.update({
                "Deprecation": "true",
                "Warning": f"299 - \"API version {version.value} is deprecated. {warning['message']}\""
            })
        return response_headers


# Middleware for version handling
class VersioningMiddleware:
    """Middleware to handle API versioning."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract version from request
            request = Request(scope, receive)
            version = get_api_version(request)
            
            # Add version to request state
            scope["state"] = getattr(scope, "state", {})
            scope["state"]["api_version"] = version
            
            # Check if version is supported
            if not APIVersionManager.is_version_supported(version):
                # Return version not supported error
                response = {
                    "error": f"API version {version.value} is not supported",
                    "supported_versions": [v.value for v in APIVersionManager.SUPPORTED_VERSIONS]
                }
                await send({
                    "type": "http.response.start",
                    "status": 400,
                    "headers": [[b"content-type", b"application/json"]]
                })
                await send({
                    "type": "http.response.body",
                    "body": str(response).encode()
                })
                return
        
        await self.app(scope, receive, send)


# Version compatibility helpers
def version_compatible(min_version: APIVersion):
    """Decorator to mark endpoints as compatible with specific versions."""
    def decorator(func):
        func._min_version = min_version
        return func
    return decorator


def version_deprecated(deprecated_in: APIVersion, removal_in: APIVersion, message: str = None):
    """Decorator to mark endpoints as deprecated."""
    def decorator(func):
        func._deprecated_in = deprecated_in
        func._removal_in = removal_in
        func._deprecation_message = message
        return func
    return decorator


# Export commonly used components
__all__ = [
    "APIVersion",
    "APIVersionManager", 
    "get_api_version",
    "VersionedResponse",
    "DeprecationManager",
    "VersioningMiddleware",
    "version_compatible",
    "version_deprecated"
]
