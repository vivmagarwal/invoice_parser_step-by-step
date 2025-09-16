from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.api import users, auth

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="Invoice Parser API",
    description="AI-powered invoice data extraction",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development/teaching
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router, prefix="/api")

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Invoice Parser API",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for frontend connection"""
    return {
        "message": "API is working!",
        "data": {
            "feature": "Invoice parsing coming soon",
            "supported_formats": ["jpg", "png", "pdf"]
        }
    }