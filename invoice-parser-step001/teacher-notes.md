# STEP-001: Basic FastAPI Hello World - Teacher Notes

## Overview
This step introduces students to FastAPI, the foundation of our backend API. Students start with an empty project and build their first working API with automatic documentation.

## Learning Objectives
1. Understand FastAPI basics and async programming
2. Learn how to structure a Python web API project
3. Configure CORS for frontend-backend communication
4. Experience automatic API documentation

## Starting Point
- **starting-code/**: Empty directory (students start from scratch)
- Students have never worked with FastAPI before
- Assume basic Python knowledge

## Ending Point
- **ending-code/backend/**: Fully working FastAPI application with:
  - Three working endpoints (/, /health, /api/test)
  - CORS middleware configured
  - Automatic documentation at /docs and /redoc
  - Virtual environment with dependencies

## Key Teaching Points

### 1. Project Structure
Emphasize the importance of:
- Virtual environments for dependency isolation
- Proper directory structure from the start
- requirements.txt for reproducible environments

### 2. FastAPI Concepts
- **Decorators**: How `@app.get()` defines routes
- **Async/Await**: Why we use `async def` for handlers
- **Automatic validation**: Type hints provide validation
- **Documentation**: Free API docs without extra work

### 3. CORS Understanding
Students often struggle with CORS. Explain:
- Why browsers enforce same-origin policy
- How CORS headers allow cross-origin requests
- Why we need it for frontend-backend communication

## Common Student Issues

### Issue 1: Virtual Environment Not Activated
**Symptom**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Remind to activate venv before installing/running

### Issue 2: Port Already in Use
**Symptom**: `[Errno 48] Address already in use`
**Solution**: Check for other processes or use different port

### Issue 3: CORS Not Working
**Symptom**: Frontend can't connect to backend
**Solution**: Verify CORS origins match frontend URL exactly

## Step-by-Step Instructions to Run and Test ending-code

### Setup Instructions
1. **Navigate to the ending-code directory**:
   ```bash
   cd invoice-parser-step001/ending-code/backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   Expected output:
   ```
   INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO: Started reloader process [####] using WatchFiles
   INFO: Started server process [####]
   INFO: Waiting for application startup.
   INFO: Application startup complete.
   ```

### Manual Testing Instructions

#### Test 1: Root Endpoint
1. **Using Browser**:
   - Open http://localhost:8000/
   - You should see JSON response:
   ```json
   {
     "message": "Welcome to Invoice Parser API",
     "timestamp": "2025-01-16T10:30:00.123456",
     "version": "0.1.0"
   }
   ```

2. **Using curl**:
   ```bash
   curl http://localhost:8000/
   ```

#### Test 2: Health Check Endpoint
1. **Using Browser**:
   - Open http://localhost:8000/health
   - You should see JSON response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-01-16T10:30:00.123456"
   }
   ```

2. **Using curl**:
   ```bash
   curl http://localhost:8000/health
   ```

#### Test 3: API Test Endpoint
1. **Using Browser**:
   - Open http://localhost:8000/api/test
   - You should see JSON response:
   ```json
   {
     "message": "API is working!",
     "data": {
       "feature": "Invoice parsing coming soon",
       "supported_formats": ["jpg", "png", "pdf"]
     }
   }
   ```

2. **Using curl**:
   ```bash
   curl http://localhost:8000/api/test
   ```

#### Test 4: API Documentation
1. **Swagger UI**:
   - Open http://localhost:8000/docs
   - You should see interactive API documentation
   - Try executing each endpoint from the UI

2. **ReDoc**:
   - Open http://localhost:8000/redoc
   - You should see alternative API documentation

### Verification Checklist
- [ ] Server starts without errors
- [ ] Root endpoint (/) returns welcome message
- [ ] Health endpoint (/health) returns status
- [ ] API test endpoint (/api/test) returns data
- [ ] Swagger docs load at /docs
- [ ] ReDoc loads at /redoc
- [ ] All endpoints return proper JSON
- [ ] No console errors in terminal

### Troubleshooting Common Issues
1. **If port 8000 is in use**: Use `--port 8001` instead
2. **If module not found**: Ensure virtual environment is activated
3. **If permission denied**: Check file permissions or use `python -m uvicorn`

## Demonstration Flow

1. **Start with Why**: Explain we're building the API brain of our invoice parser
2. **Show the End Goal**: Demo the working API and documentation
3. **Build Step by Step**:
   - Create directories manually (builds muscle memory)
   - Explain each line as you write it
   - Test immediately after each endpoint
4. **Let Students Explore**: Have them add their own test endpoint
5. **Debug Together**: Intentionally make a CORS error and fix it

## Assessment Checkpoints
✅ Server starts without errors
✅ All three endpoints return correct JSON
✅ /docs and /redoc load properly
✅ Student can explain what async/await does
✅ Student can add a new endpoint independently

## Extensions for Advanced Students
- Add request/response models with Pydantic
- Implement query parameters
- Add basic error handling
- Create a POST endpoint

## Connection to Next Step
The ending-code of this step becomes the starting-code for STEP-002. Students will:
- Keep the backend running
- Add a React frontend that connects to these endpoints
- See their API in action with a real UI

## Time Management
- 15 min: Explain concepts and show demo
- 30 min: Build together
- 20 min: Students practice
- 10 min: Debug common issues
- 15 min: Add custom endpoint

## Key Vocabulary
- **API**: Application Programming Interface
- **Endpoint**: Specific URL path that handles requests
- **CORS**: Cross-Origin Resource Sharing
- **Async**: Non-blocking code execution
- **Middleware**: Code that runs before/after requests

## Success Metrics
Students successfully complete this step when they:
1. Have a working FastAPI server
2. Can access all endpoints via curl or browser
3. Understand why we use async functions
4. Can explain what CORS does
5. Successfully add their own endpoint