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

    # AI Configuration
    GEMINI_API_KEY: Optional[str] = None
    USE_MOCK_AI: bool = False  # Set to True to use mock AI for testing without API key

    class Config:
        env_file = ".env"

settings = Settings()