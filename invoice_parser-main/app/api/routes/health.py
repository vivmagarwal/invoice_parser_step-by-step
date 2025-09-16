"""
Health Check Routes

Provides system health monitoring endpoints.
"""
from datetime import datetime
from fastapi import APIRouter, Depends

from app.core.config import get_settings
# Migration manager removed - using simple SQLAlchemy table creation
from app.core.versioning import APIVersionManager
from app.core.monitoring import get_metrics_endpoint, system_monitor
from app.core.security_headers import get_security_headers_info
from app.api.dependencies import get_invoice_service, get_database_health

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db_health: dict = Depends(get_database_health),
    invoice_service = Depends(get_invoice_service)
):
    """
    Comprehensive health check endpoint.
    
    Returns status of all system components:
    - API server
    - AI model availability  
    - Database connectivity
    - Service components
    """
    settings = get_settings()
    
    # Get service status
    service_status = invoice_service.get_service_status()
    
    # Build health response
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        
        # AI Model Status
        "gemini_available": service_status["components"]["ai_available"],
        "ai_model": service_status["ai_processor"]["model_name"],
        
        # Database Status
        "database_connected": db_health["database_connected"],
        "database_url_configured": db_health["database_url_configured"],
        
        # Service Status
        "service_components": service_status["components"],
        "database_stats": service_status.get("database", {}),
        
        # Additional Info
        "message": db_health.get("message", "System operational")
    }
    
    return health_data


@router.get("/health/simple")
async def simple_health_check():
    """Simple health check for load balancers."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@router.get("/health/database")
async def database_status(db_health: dict = Depends(get_database_health)):
    """Get database status and basic information."""
    return {
        "status": "healthy" if db_health["database_connected"] else "error",
        "timestamp": datetime.now().isoformat(),
        "database_info": {
            "connected": db_health["database_connected"],
            "url_configured": db_health["database_url_configured"],
            "message": db_health.get("message", "Database status unknown")
        }
    }


@router.get("/version")
async def api_version_info():
    """Get API version information."""
    settings = get_settings()
    version_info = APIVersionManager.get_version_info()
    
    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        },
        "api": version_info,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/health/system")
async def system_health():
    """Get detailed system health and performance metrics."""
    try:
        health_status = system_monitor.get_health_status()
        return health_status
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/metrics")
async def get_metrics():
    """Get application metrics for monitoring systems (Prometheus format compatible)."""
    try:
        return get_metrics_endpoint()
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/security")
async def security_info():
    """Get information about implemented security features."""
    settings = get_settings()
    
    return {
        "security_headers": get_security_headers_info(),
        "environment": settings.ENVIRONMENT,
        "security_features": {
            "rate_limiting": "Implemented with multiple strategies",
            "input_validation": "Comprehensive validation and sanitization",
            "authentication": "JWT-based with secure password hashing",
            "database_security": "Parameterized queries and connection pooling",
            "file_security": "Type validation and secure storage",
            "monitoring": "Request logging and performance tracking",
            "error_handling": "Structured error responses without information disclosure"
        },
        "timestamp": datetime.now().isoformat()
    }
