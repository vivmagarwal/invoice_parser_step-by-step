"""
Database Connection Management

Handles PostgreSQL connections via SQLAlchemy with proper error handling,
connection pooling, and session management.
"""
import logging
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.core.config import get_settings, get_database_config
from app.models.database import Base

# Configure logging
logger = logging.getLogger(__name__)

# Global engine and session factory
engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker] = None


def get_database_engine() -> Engine:
    """Get or create database engine with connection pooling."""
    global engine
    if engine is None:
        settings = get_settings()
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL not configured")
        
        try:
            db_config = get_database_config()
            engine = create_engine(
                settings.DATABASE_URL,
                **db_config
            )
            logger.info(f"Database engine created successfully with config: {db_config}")
            logger.info(f"Pool size: {db_config['pool_size']}, Max overflow: {db_config['max_overflow']}")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    
    return engine


def get_session_factory() -> sessionmaker:
    """Get or create session factory."""
    global SessionLocal
    if SessionLocal is None:
        engine = get_database_engine()
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        logger.info("Session factory created successfully")
    
    return SessionLocal


@contextmanager
def get_db_session():
    """Context manager for database sessions with automatic cleanup."""
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def create_tables() -> bool:
    """Create all database tables."""
    try:
        engine = get_database_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False


def health_check_db() -> dict[str, any]:
    """Check database connection health."""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        
        settings = get_settings()
        return {
            "database_connected": True,
            "database_url_configured": bool(settings.DATABASE_URL),
            "message": "Database connection healthy"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        settings = get_settings()
        return {
            "database_connected": False,
            "database_url_configured": bool(settings.DATABASE_URL),
            "message": f"Database connection failed: {str(e)}"
        }


# Initialize database on module import
def initialize_database():
    """Initialize database connection and create tables if needed."""
    try:
        settings = get_settings()
        if settings.DATABASE_URL:
            create_tables()
            logger.info("Database initialized successfully")
        else:
            logger.warning("DATABASE_URL not configured - database features disabled")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


# Auto-initialize when module is imported (except during testing)
if __name__ != "__main__":
    initialize_database()
