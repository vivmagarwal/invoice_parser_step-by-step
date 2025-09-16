# STEP-001: Basic FastAPI Hello World

## Directory Structure
```
invoice-parser-step001/
├── starting-code/      # Empty - students start from scratch
├── ending-code/        # Complete working FastAPI application
├── teacher-notes.md    # Detailed teaching guide with run instructions
└── README.md          # This file
```

## Quick Start (for Teachers/Testing)

To run and test the completed code:

```bash
# 1. Navigate to ending-code
cd ending-code/backend

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn app.main:app --reload --port 8000

# 5. Test the endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/api/test

# 6. View API documentation
open http://localhost:8000/docs
```

## For Detailed Instructions
See `teacher-notes.md` for:
- Complete setup instructions
- Manual testing for all features
- Expected outputs
- Common issues and solutions
- Teaching guidance

## Learning Objectives
- Understand FastAPI basics
- Learn async programming in Python
- Configure CORS for frontend communication
- Experience automatic API documentation

## What Students Build
Starting from an empty directory, students create:
- A working FastAPI application
- Three API endpoints (/, /health, /api/test)
- CORS middleware configuration
- Automatic documentation at /docs and /redoc