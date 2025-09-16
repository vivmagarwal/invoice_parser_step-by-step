from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Invoice Parser API"
    DEBUG: bool = True

    # Database - using SQLite for simplicity in teaching
    DATABASE_URL: str = "sqlite+aiosqlite:///./invoice_parser.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    class Config:
        env_file = ".env"

settings = Settings()