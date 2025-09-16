"""
FastAPI Dependencies

Provides dependency injection for services and database sessions.
"""
from functools import lru_cache

from app.services.invoice_service import InvoiceService
from app.services.database_service import DatabaseService
from app.services.auth_service import AuthService
from app.services.file_service import FileService
from app.core.ai_processor import AIProcessor
from app.core.database import health_check_db


@lru_cache()
def get_invoice_service() -> InvoiceService:
    """Get invoice service instance (cached)."""
    return InvoiceService()


@lru_cache()
def get_database_service() -> DatabaseService:
    """Get database service instance (cached)."""
    return DatabaseService()


@lru_cache()
def get_ai_processor() -> AIProcessor:
    """Get AI processor instance (cached)."""
    return AIProcessor()


@lru_cache()
def get_auth_service() -> AuthService:
    """Get authentication service instance (cached)."""
    return AuthService()


@lru_cache()
def get_file_service() -> FileService:
    """Get file service instance (cached)."""
    return FileService()


def get_database_health() -> dict:
    """Get database health status."""
    return health_check_db()
