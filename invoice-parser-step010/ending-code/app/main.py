"""
FastAPI Application Entry Point

Clean, modular FastAPI application with organized route structure
and proper dependency injection.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import get_settings
# Simple database initialization without Alembic
async def init_database():
    """Initialize database tables using SQLAlchemy."""
    try:
        from app.core.database import get_database_engine
        from app.models.database import Base
        
        engine = get_database_engine()
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
from app.core.logging_config import setup_logging, RequestLoggingMiddleware
from app.core.monitoring import start_monitoring, stop_monitoring
from app.core.rate_limiting import create_production_rate_limiter
from app.core.security_headers import create_security_middleware
from app.core.exceptions import (
    BaseAppException,
    base_app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.api.routes import health, invoices, auth, dashboard, user, files, static_files, analytics, websocket, search, bulk, ai_insights

# Configure structured logging
settings = get_settings()
setup_logging(environment=settings.ENVIRONMENT, log_level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize any startup tasks here
    try:
        # Database initialization happens automatically via imports
        logger.info("Initializing database...")
        
        # Initialize database tables
        db_success = await init_database()
        if not db_success:
            logger.error("Database initialization failed during startup")
            raise RuntimeError("Database initialization failed")
        
        # Start monitoring
        logger.info("Starting application monitoring...")
        await start_monitoring()
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down monitoring...")
    stop_monitoring()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # Add middleware in correct order (CORS first, then logging)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # React dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add rate limiting middleware (after logging for proper monitoring)
    rate_limiter = create_production_rate_limiter()
    app.add_middleware(type(rate_limiter), backend=rate_limiter.backend, rules=rate_limiter.rules)
    
    # Add security headers middleware (last in chain for outbound processing)
    security_middleware = create_security_middleware(environment=settings.ENVIRONMENT)
    app.add_middleware(type(security_middleware), 
                      csp_policy=security_middleware._get_default_csp_policy(),
                      environment=settings.ENVIRONMENT)
    
    # Include routers with versioning
    # V1 API routes
    app.include_router(health.router, prefix="/api/v1", tags=["v1"])
    app.include_router(auth.router, prefix="/api/v1", tags=["v1"])
    app.include_router(user.router, prefix="/api/v1", tags=["v1"])
    app.include_router(files.router, prefix="/api/v1", tags=["v1"])
    app.include_router(dashboard.router, prefix="/api/v1", tags=["v1"])
    app.include_router(invoices.router, prefix="/api/v1", tags=["v1"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["v1"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["v1"])
    app.include_router(search.router, prefix="/api/v1", tags=["v1"])
    app.include_router(bulk.router, prefix="/api/v1", tags=["v1"])
    app.include_router(ai_insights.router, prefix="/api/v1", tags=["v1"])
    
    # Backward compatibility - include routers without version for existing clients
    app.include_router(health.router, prefix="/api", tags=["legacy"])
    app.include_router(auth.router, prefix="/api", tags=["legacy"])
    app.include_router(user.router, prefix="/api", tags=["legacy"])
    app.include_router(files.router, prefix="/api", tags=["legacy"])
    app.include_router(dashboard.router, prefix="/api", tags=["legacy"])
    app.include_router(invoices.router, prefix="/api", tags=["legacy"])
    app.include_router(analytics.router, prefix="/api", tags=["legacy"])
    app.include_router(websocket.router, prefix="/api", tags=["legacy"])
    app.include_router(search.router, prefix="/api", tags=["legacy"])
    app.include_router(bulk.router, prefix="/api", tags=["legacy"])
    app.include_router(ai_insights.router, prefix="/api", tags=["legacy"])
    
    # Static and homepage routes (no versioning)
    app.include_router(static_files.router)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Add exception handlers
    app.add_exception_handler(BaseAppException, base_app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
