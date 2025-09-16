from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Invoice Parser API",
    description="AI-powered invoice data extraction",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development/teaching
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

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