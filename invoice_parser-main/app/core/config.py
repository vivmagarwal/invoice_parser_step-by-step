"""
Application Configuration Management

Centralized configuration using Pydantic Settings with environment variable support.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Info
    APP_NAME: str = "Invoice Parser"
    APP_DESCRIPTION: str = "AI-powered invoice parser with database persistence"
    VERSION: str = "0.1.0"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API Configuration
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/invoice_parser"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False
    DB_ECHO_POOL: bool = False
    
    # Connection retry configuration
    DB_MAX_RETRIES: int = 3
    DB_RETRY_DELAY: float = 1.0
    
    # Query timeout configuration
    DB_QUERY_TIMEOUT: int = 30
    DB_STATEMENT_TIMEOUT: int = 60
    
    # AI Configuration
    GOOGLE_API_KEY: str = "your-google-api-key-here"
    AI_MODEL_NAME: str = "gemini-2.0-flash"
    AI_TEMPERATURE: float = 0.0
    
    # Authentication Configuration
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list[str] = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Allow extra fields from environment
    }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings


def get_database_config() -> dict:
    """Get optimized database configuration based on environment."""
    config = {
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": settings.DB_POOL_PRE_PING,
        "echo": settings.DB_ECHO,
        "echo_pool": settings.DB_ECHO_POOL,
    }
    
    # Environment-specific optimizations
    if settings.ENVIRONMENT == "production":
        config.update({
            "pool_size": max(10, settings.DB_POOL_SIZE),
            "max_overflow": max(20, settings.DB_MAX_OVERFLOW),
            "pool_timeout": 60,
            "pool_recycle": 7200,  # 2 hours in production
        })
    elif settings.ENVIRONMENT == "development":
        config.update({
            "pool_size": 3,
            "max_overflow": 5,
            "echo": settings.DEBUG,
            "echo_pool": settings.DEBUG,
        })
    elif settings.ENVIRONMENT == "testing":
        config.update({
            "pool_size": 1,
            "max_overflow": 2,
            "pool_timeout": 10,
            "echo": False,
        })
    
    return config
