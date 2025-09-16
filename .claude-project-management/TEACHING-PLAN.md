# Invoice Parser AI - Progressive Teaching Plan

## Usage Instructions
1. **ALWAYS** read this plan at every session start
2. Update YAML status after **EACH** step completion
3. Document all discoveries inline
4. This document + codebase = complete learning resource
5. **NEVER** skip updating the progress tracking

## Target Audience
- Absolute beginners with basic programming knowledge
- No framework-specific experience required
- Learning by building, not just reading

## Teaching Philosophy
- One concept per step
- Working application after every step
- Test everything before proceeding
- Document the "why" not just "how"
- Build confidence through incremental success

## Progress Tracking

```yaml
teaching_progress:
  current_step: 7
  total_steps: 10
  last_updated: "2025-09-16T16:30:00Z"
  environment_ready: true

  setup_checklist:
    python_installed: false
    node_installed: false
    postgres_setup: false
    gemini_api_key: false
    project_cloned: false

steps:
  - step_id: "STEP-001"
    title: "Basic FastAPI Hello World"
    description: "Create minimal FastAPI server with one endpoint"

    pre_implementation:
      previous_step_complete: true
      environment_ready: false
      concepts_explained: false
      starter_code_provided: false

    learning_objectives:
      - objective: "Understand FastAPI basics"
        achieved: false
      - objective: "Learn about async/await"
        achieved: false
      - objective: "Use automatic API docs"
        achieved: false

    implementation_checklist:
      files_created: false
      dependencies_installed: false
      code_written: false
      manually_tested: false
      playwright_tested: false

    post_implementation:
      app_working: false
      tests_passing: false
      concepts_understood: false
      ready_for_next: false

    implementation_status: "not_started"

    implementation_notes: |
      [Session notes will go here]

    learner_feedback: |
      [Common issues and solutions]

  - step_id: "STEP-002"
    title: "React Frontend with Vite"
    description: "Create React app that fetches from FastAPI"

    pre_implementation:
      previous_step_complete: false
      environment_ready: false
      concepts_explained: false
      starter_code_provided: false

    learning_objectives:
      - objective: "Set up React with Vite"
        achieved: false
      - objective: "Create first component"
        achieved: false
      - objective: "Fetch data from API"
        achieved: false

    implementation_checklist:
      files_created: false
      dependencies_installed: false
      code_written: false
      manually_tested: false
      playwright_tested: false

    post_implementation:
      app_working: false
      tests_passing: false
      concepts_understood: false
      ready_for_next: false

    implementation_status: "not_started"

    implementation_notes: |
      [Session notes]

    learner_feedback: |
      [Issues and solutions]

  - step_id: "STEP-003"
    title: "Tailwind Styling & Dark Mode"
    description: "Add Tailwind CSS and implement theme switching"

    pre_implementation:
      previous_step_complete: false
      environment_ready: false
      concepts_explained: false
      starter_code_provided: false

    learning_objectives:
      - objective: "Install and configure Tailwind"
        achieved: false
      - objective: "Apply utility classes"
        achieved: false
      - objective: "Implement dark mode toggle"
        achieved: false

    implementation_checklist:
      files_created: false
      dependencies_installed: false
      code_written: false
      manually_tested: false
      playwright_tested: false

    post_implementation:
      app_working: false
      tests_passing: false
      concepts_understood: false
      ready_for_next: false

    implementation_status: "not_started"

    implementation_notes: |
      [Session notes]

    learner_feedback: |
      [Issues and solutions]

  - step_id: "STEP-004"
    title: "PostgreSQL Database Setup"
    description: "Add SQLAlchemy and create first models"

    pre_implementation:
      previous_step_complete: true
      environment_ready: true
      concepts_explained: true
      starter_code_provided: true

    learning_objectives:
      - objective: "Set up SQLite/PostgreSQL database"
        achieved: true
      - objective: "Create SQLAlchemy models"
        achieved: true
      - objective: "Implement CRUD operations"
        achieved: true

    implementation_checklist:
      files_created: true
      dependencies_installed: true
      code_written: true
      manually_tested: true
      playwright_tested: false

    post_implementation:
      app_working: true
      tests_passing: true
      concepts_understood: true
      ready_for_next: true

    implementation_status: "completed"

    implementation_notes: |
      - Successfully implemented database with SQLAlchemy async support
      - Used SQLite for simplicity (easily switchable to PostgreSQL)
      - Created User model with secure password hashing using bcrypt
      - Implemented complete CRUD operations for users
      - Added proper Pydantic schemas for validation
      - Service layer pattern for business logic separation
      - Dependencies: aiosqlite, greenlet, email-validator required
      - Database tables auto-created on startup via lifespan event
      - All endpoints tested and working correctly

    learner_feedback: |
      - Issue: Missing greenlet dependency -> Solution: Added to requirements
      - Issue: EmailStr validation error -> Solution: Added email-validator
      - Success: Database operations working smoothly with async/await

  - step_id: "STEP-005"
    title: "User Authentication"
    description: "Implement JWT auth with registration and login"

    pre_implementation:
      previous_step_complete: true
      environment_ready: true
      concepts_explained: true
      starter_code_provided: true

    learning_objectives:
      - objective: "Understand JWT tokens"
        achieved: true
      - objective: "Implement password hashing"
        achieved: true
      - objective: "Create protected routes"
        achieved: true

    implementation_checklist:
      files_created: true
      dependencies_installed: true
      code_written: true
      manually_tested: true
      playwright_tested: false

    post_implementation:
      app_working: true
      tests_passing: true
      concepts_understood: true
      ready_for_next: true

    implementation_status: "completed"

    implementation_notes: |
      Successfully implemented JWT authentication with:
      - python-jose for JWT token handling
      - OAuth2PasswordRequestForm for standard login flow
      - Bearer token authentication
      - Protected routes with authentication dependencies
      - User registration, login, and profile endpoints
      - Modified authenticate_user to support email or username
      - Authorization logic for user updates/deletes
      - Comprehensive test script validating all flows

    learner_feedback: |
      - Important: OAuth2PasswordRequestForm expects form data, not JSON
      - Token should be in Authorization header as "Bearer {token}"
      - SECRET_KEY must be in .env file for JWT encoding
      - Authentication works with both email and username

  - step_id: "STEP-006"
    title: "File Upload System"
    description: "Add file upload with validation and storage"

    pre_implementation:
      previous_step_complete: true
      environment_ready: true
      concepts_explained: true
      starter_code_provided: true

    learning_objectives:
      - objective: "Handle file uploads safely"
        achieved: true
      - objective: "Validate file types/sizes"
        achieved: true
      - objective: "Store files with user isolation"
        achieved: true

    implementation_checklist:
      files_created: true
      dependencies_installed: true
      code_written: true
      manually_tested: true
      playwright_tested: false

    post_implementation:
      app_working: true
      tests_passing: true
      concepts_understood: true
      ready_for_next: true

    implementation_status: "completed"

    implementation_notes: |
      Successfully implemented secure file upload system:
      - Invoice model with file metadata and processing status
      - FileService for validation and storage with UUID naming
      - InvoiceService for CRUD operations
      - API endpoints for upload, list, get, delete
      - User-isolated storage directories
      - File type validation (PDF, JPG, JPEG, PNG)
      - Size limit enforcement (10MB)
      - Async file operations with aiofiles
      - Comprehensive test suite validates all functionality

    learner_feedback: |
      - Important: Use multipart/form-data for file uploads, not JSON
      - Create upload directories with parents=True
      - Clean up files on error to prevent orphans
      - Import models in main.py to register with SQLAlchemy
      - Check file size during chunked reading, not after

  - step_id: "STEP-007"
    title: "AI Integration - Gemini API"
    description: "Connect Google Gemini for invoice parsing"

    pre_implementation:
      previous_step_complete: true
      environment_ready: true
      concepts_explained: true
      starter_code_provided: true

    learning_objectives:
      - objective: "Set up Gemini API"
        achieved: true
      - objective: "Use LangChain for structured output"
        achieved: true
      - objective: "Handle AI errors gracefully"
        achieved: true

    implementation_checklist:
      files_created: true
      dependencies_installed: true
      code_written: true
      manually_tested: true
      playwright_tested: false

    post_implementation:
      app_working: true
      tests_passing: true
      concepts_understood: true
      ready_for_next: true

    implementation_status: "completed"

    implementation_notes: |
      - Successfully implemented AI service abstraction with interface pattern
      - Created both MockAIService and GeminiAIService implementations
      - Used factory pattern for service selection based on configuration
      - Integrated LangChain for structured output parsing with Pydantic models
      - Added comprehensive error handling with tenacity retry logic
      - Implemented invoice processing endpoint with status tracking
      - Created test script that works with mock AI (no API key needed)
      - Added support for both image and PDF processing
      - Stored extracted data as JSON in database
      - Dependencies: google-generativeai, langchain, langchain-google-genai, pillow, pypdf, pdf2image

    learner_feedback: |
      - Mock AI service allows testing without API keys - great for learning
      - Factory pattern makes switching between mock/real AI seamless
      - Status tracking (pending→processing→completed/failed) provides good UX
      - Retry logic with exponential backoff handles API failures gracefully
      - Structured output with LangChain ensures consistent data format

  - step_id: "STEP-008"
    title: "Complete Invoice Processing"
    description: "Build full invoice data extraction pipeline"

    pre_implementation:
      previous_step_complete: false
      environment_ready: false
      concepts_explained: false
      starter_code_provided: false

    learning_objectives:
      - objective: "Create complete data models"
        achieved: false
      - objective: "Implement processing pipeline"
        achieved: false
      - objective: "Save parsed data to database"
        achieved: false

    implementation_checklist:
      files_created: false
      dependencies_installed: false
      code_written: false
      manually_tested: false
      playwright_tested: false

    post_implementation:
      app_working: false
      tests_passing: false
      concepts_understood: false
      ready_for_next: false

    implementation_status: "not_started"

    implementation_notes: |
      [Session notes]

    learner_feedback: |
      [Issues and solutions]

  - step_id: "STEP-009"
    title: "Dashboard & Analytics"
    description: "Create user dashboard with statistics"

    pre_implementation:
      previous_step_complete: false
      environment_ready: false
      concepts_explained: false
      starter_code_provided: false

    learning_objectives:
      - objective: "Build dashboard UI"
        achieved: false
      - objective: "Aggregate statistics"
        achieved: false
      - objective: "Implement pagination"
        achieved: false

    implementation_checklist:
      files_created: false
      dependencies_installed: false
      code_written: false
      manually_tested: false
      playwright_tested: false

    post_implementation:
      app_working: false
      tests_passing: false
      concepts_understood: false
      ready_for_next: false

    implementation_status: "not_started"

    implementation_notes: |
      [Session notes]

    learner_feedback: |
      [Issues and solutions]

  - step_id: "STEP-010"
    title: "Polish & Production Ready"
    description: "Error handling, monitoring, and deployment prep"

    pre_implementation:
      previous_step_complete: false
      environment_ready: false
      concepts_explained: false
      starter_code_provided: false

    learning_objectives:
      - objective: "Add comprehensive error handling"
        achieved: false
      - objective: "Implement logging and monitoring"
        achieved: false
      - objective: "Prepare for deployment"
        achieved: false

    implementation_checklist:
      files_created: false
      dependencies_installed: false
      code_written: false
      manually_tested: false
      playwright_tested: false

    post_implementation:
      app_working: false
      tests_passing: false
      concepts_understood: false
      ready_for_next: false

    implementation_status: "not_started"

    implementation_notes: |
      [Session notes]

    learner_feedback: |
      [Issues and solutions]
```

## CRITICAL: Step Directory Structure Requirements

### Every Step MUST Follow This Structure:
```
invoice-parser-stepXXX/
├── starting-code/      # Copy of previous step's ending-code (empty for step 001)
├── ending-code/        # Complete working code when step is finished
└── teacher-notes.md    # Teaching guidance, common issues, and solutions
```

### Key Rules:
1. **Continuity**: The `ending-code` of step N becomes the `starting-code` of step N+1
2. **No Gaps**: Each step builds directly on the previous - no missing pieces
3. **Teacher Notes**: Must include learning objectives, common issues, and assessment points
4. **Testing**: Each step's ending-code must be fully functional and tested

### MANDATORY: Teacher Notes Must Include Run & Test Instructions
Every `teacher-notes.md` file MUST contain:
1. **Setup Instructions**: Step-by-step commands to set up the environment
2. **Run Instructions**: Exact commands to start the application
3. **Manual Testing Guide**:
   - How to test EVERY feature in the ending-code
   - Expected output for each test
   - Both browser and curl commands where applicable
4. **Verification Checklist**: List of items to verify everything works
5. **Troubleshooting Guide**: Common issues and their solutions

**WITHOUT THESE INSTRUCTIONS, A STEP IS NOT COMPLETE!**

## Step Definitions

### STEP-001: Basic FastAPI Hello World ✅ COMPLETED
**Starting Code**: Empty project
**Ending Code**: Working API with documentation
**Time Estimate**: 2-3 hours
**Completion Date**: 2025-09-16
**Implementation Location**: `/invoice-parser-step001/`

<lesson>
#### Why This Step Matters
FastAPI is the foundation of our backend. We start here to understand how modern Python web APIs work, introducing async programming and automatic documentation.

#### What You'll Build
```
backend/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
└── .env.example
```

#### Concepts to Master
1. **FastAPI Basics**: Routes, path parameters, response models
2. **Async/Await**: Why Python async matters for web APIs
3. **Automatic Documentation**: Swagger UI and ReDoc
4. **Uvicorn Server**: ASGI and hot reload

#### Implementation Guide

**1. Create Project Structure:**
```bash
mkdir invoice-parser
cd invoice-parser
mkdir -p backend/app
cd backend
```

**2. Set Up Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Create requirements.txt:**
```txt
fastapi==0.115.14
uvicorn[standard]==0.34.0
python-dotenv==1.0.1
```

**4. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**5. Create app/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Create FastAPI instance
app = FastAPI(
    title="Invoice Parser API",
    description="AI-powered invoice data extraction",
    version="0.1.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
```

**6. Create .env.example:**
```env
# Application
APP_NAME=Invoice Parser
ENVIRONMENT=development
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000
```

**7. Run the Server:**
```bash
uvicorn app.main:app --reload --port 8000
```

#### Understanding the Code

**FastAPI Instance:**
- `app = FastAPI()` creates our application
- Metadata helps with documentation
- Instance handles all routing

**CORS Middleware:**
- Allows frontend to communicate with backend
- Security feature for cross-origin requests
- Must match frontend URL

**Async Functions:**
- `async def` allows handling multiple requests
- More efficient than synchronous code
- Required for database operations later

**Decorators:**
- `@app.get("/")` defines HTTP method and path
- FastAPI uses these to build routes
- Automatic validation and documentation

#### Testing This Step

**Manual Testing:**
1. Visit http://localhost:8000 - See JSON response
2. Visit http://localhost:8000/docs - Interactive API docs
3. Visit http://localhost:8000/redoc - Alternative docs

**Automated Testing with curl:**
```bash
# Test root endpoint
curl http://localhost:8000/

# Test health endpoint
curl http://localhost:8000/health

# Test API endpoint
curl http://localhost:8000/api/test
```

**Expected Output:**
```json
{
  "message": "Welcome to Invoice Parser API",
  "timestamp": "2025-01-16T10:30:00.123456",
  "version": "0.1.0"
}
```

#### Common Issues & Solutions

**Issue 1: Port Already in Use**
```
ERROR: [Errno 48] Address already in use
```
**Solution:** Change port or kill existing process:
```bash
uvicorn app.main:app --reload --port 8001
```

**Issue 2: Module Not Found**
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:** Activate virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Issue 3: CORS Errors (Later with Frontend)**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked
```
**Solution:** Check CORS middleware configuration matches frontend URL

#### Checklist Before Next Step
- [ ] Server runs without errors
- [ ] All three endpoints return data
- [ ] API documentation loads at /docs
- [ ] Understood async/await basics
- [ ] Can modify and add new endpoints

#### Key Takeaways
1. FastAPI provides automatic validation and docs
2. Async functions handle concurrent requests
3. CORS is essential for frontend-backend communication
4. Good project structure matters from the start
</lesson>

### STEP-002: React Frontend with Vite ✅ COMPLETED
**Starting Code**: Working FastAPI backend
**Ending Code**: React app fetching from API
**Time Estimate**: 3-4 hours
**Completion Date**: 2025-09-16
**Implementation Location**: `/invoice-parser-step002/`

<lesson>
#### Why This Step Matters
The frontend is how users interact with our AI invoice parser. React with Vite provides a modern, fast development experience with hot module replacement.

#### What You'll Build
```
frontend/
├── public/
├── src/
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
└── .env.example
```

#### Implementation Guide

**1. Create React App with Vite:**
```bash
# From project root
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

**2. Install Additional Dependencies:**
```bash
npm install axios
```

**3. Configure Vite (vite.config.js):**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

**4. Create Basic App Structure (src/App.jsx):**
```jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [apiData, setApiData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchApiData()
  }, [])

  const fetchApiData = async () => {
    try {
      setLoading(true)
      const response = await axios.get('http://localhost:8000/api/test')
      setApiData(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to connect to API')
      console.error('API Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Invoice Parser AI</h1>
        <p>Upload invoices and extract data automatically</p>
      </header>

      <main className="app-main">
        <div className="status-card">
          <h2>API Status</h2>
          {loading && <p>Loading...</p>}
          {error && <p className="error">{error}</p>}
          {apiData && (
            <div className="api-info">
              <p className="success">✓ Connected to API</p>
              <p>{apiData.message}</p>
              <div className="features">
                <h3>Features:</h3>
                <p>{apiData.data.feature}</p>
                <p>Supported formats: {apiData.data.supported_formats.join(', ')}</p>
              </div>
            </div>
          )}
          <button onClick={fetchApiData}>Refresh</button>
        </div>
      </main>
    </div>
  )
}

export default App
```

**5. Add Basic Styling (src/App.css):**
```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.app-header h1 {
  margin: 0;
  font-size: 2.5rem;
}

.app-header p {
  margin: 0.5rem 0 0;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: #f5f5f5;
}

.status-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 400px;
}

.status-card h2 {
  margin-top: 0;
  color: #333;
}

.error {
  color: #d32f2f;
  font-weight: bold;
}

.success {
  color: #2e7d32;
  font-weight: bold;
}

.api-info {
  margin: 1rem 0;
}

.features {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.features h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
}

button:hover {
  background: #5a67d8;
}
```

**6. Run Both Backend and Frontend:**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

#### Understanding the Code

**React Hooks:**
- `useState`: Manages component state
- `useEffect`: Handles side effects (API calls)
- Hooks replace class components

**Async Data Fetching:**
- axios makes HTTP requests
- async/await for cleaner code
- Error handling with try/catch

**Conditional Rendering:**
- Show different UI based on state
- Loading, error, and success states
- User feedback is crucial

#### Testing This Step

**Manual Testing:**
1. Open http://localhost:5173
2. Should see "Connected to API"
3. Click Refresh button
4. Check browser console for errors

**Browser DevTools Testing:**
1. Open Network tab
2. Refresh page
3. See API call to localhost:8000
4. Check response data

#### Common Issues & Solutions

**Issue: CORS Error**
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution:** Ensure backend CORS allows http://localhost:5173

**Issue: Connection Refused**
```
Error: Network Error at http://localhost:8000
```
**Solution:** Make sure backend is running on port 8000

**Issue: Blank Page**
```
Page loads but nothing appears
```
**Solution:** Check browser console for React errors

#### Checklist Before Next Step
- [ ] Frontend loads without errors
- [ ] Successfully connects to backend API
- [ ] Refresh button works
- [ ] Styling appears correctly
- [ ] Both servers run simultaneously
</lesson>

### STEP-003: Tailwind Styling & Dark Mode ✅ COMPLETED
**Starting Code**: Basic React app with CSS
**Ending Code**: Tailwind-styled app with theme toggle
**Time Estimate**: 2-3 hours
**Completion Date**: 2025-09-16
**Implementation Location**: `/invoice-parser-step003/`

<lesson>
#### Why This Step Matters
Tailwind CSS provides utility classes that speed up development. Dark mode is expected in modern applications and improves user experience.

#### Implementation Guide

**1. Install Tailwind CSS:**
```bash
cd frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**2. Configure Tailwind (tailwind.config.js):**
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**3. Replace index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**4. Create Theme Context (src/contexts/ThemeContext.jsx):**
```jsx
import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light'
    setTheme(savedTheme)
    document.documentElement.classList.toggle('dark', savedTheme === 'dark')
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

**5. Update App.jsx with Tailwind:**
```jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import { useTheme } from './contexts/ThemeContext'

function App() {
  const [apiData, setApiData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    fetchApiData()
  }, [])

  const fetchApiData = async () => {
    try {
      setLoading(true)
      const response = await axios.get('http://localhost:8000/api/test')
      setApiData(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to connect to API')
      console.error('API Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-800 dark:to-indigo-800 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">Invoice Parser AI</h1>
              <p className="text-purple-100 mt-1">Upload invoices and extract data automatically</p>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Status Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              API Status
            </h2>

            {loading && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
                <span className="text-gray-600 dark:text-gray-400">Loading...</span>
              </div>
            )}

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-red-600 dark:text-red-400 font-medium">{error}</p>
              </div>
            )}

            {apiData && (
              <div className="space-y-4">
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <p className="text-green-600 dark:text-green-400 font-medium">
                    ✓ Connected to API
                  </p>
                </div>

                <div className="text-gray-700 dark:text-gray-300">
                  <p className="text-lg">{apiData.message}</p>
                </div>

                <div className="border-t dark:border-gray-700 pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Features
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">{apiData.data.feature}</p>
                  <div className="mt-2">
                    <span className="text-sm text-gray-500 dark:text-gray-500">Supported formats: </span>
                    <div className="flex gap-2 mt-1">
                      {apiData.data.supported_formats.map(format => (
                        <span
                          key={format}
                          className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded text-sm"
                        >
                          {format}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={fetchApiData}
              className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Refresh Status
            </button>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 transition-colors">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Quick Start</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Upload your invoice images and let AI extract the data automatically.
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 transition-colors">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Secure Processing</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your data is processed securely and stored with encryption.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
```

**6. Update main.jsx:**
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { ThemeProvider } from './contexts/ThemeContext'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
```

#### Testing This Step

**Theme Toggle Testing:**
1. Click moon/sun icon
2. Page should switch themes
3. Refresh page - theme persists
4. Check localStorage has theme key

**Responsive Testing:**
1. Resize browser window
2. Cards should stack on mobile
3. Layout should adapt smoothly

#### Checklist Before Next Step
- [ ] Tailwind classes work
- [ ] Dark mode toggles properly
- [ ] Theme persists on refresh
- [ ] Responsive design works
- [ ] No styling conflicts
</lesson>

### STEP-004: PostgreSQL Database Setup
**Starting Code**: Frontend with API connection
**Ending Code**: Database with user model
**Time Estimate**: 3-4 hours

<lesson>
#### Why This Step Matters
Databases store our application data permanently. SQLAlchemy provides an ORM that makes database operations safer and easier than raw SQL.

#### Prerequisites
1. Create free Neon account at https://neon.tech
2. Create new project and get connection string
3. Note down the connection URL

#### Implementation Guide

**1. Install Database Dependencies:**
```bash
cd backend
pip install sqlalchemy asyncpg psycopg2-binary alembic
```

**2. Create Database Configuration (app/core/config.py):**
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Invoice Parser API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    class Config:
        env_file = ".env"

settings = Settings()
```

**3. Create Database Setup (app/core/database.py):**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**4. Create User Model (app/models/user.py):**
```python
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.username}>"
```

**5. Create Pydantic Schemas (app/schemas/user.py):**
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
```

**6. Create User Service (app/services/user_service.py):**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        hashed_password = UserService.hash_password(user_data.password)

        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
```

**7. Create API Routes (app/api/users.py):**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    # Check if user exists
    existing_user = await UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = await UserService.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = await UserService.create_user(db, user_data)
    return user

@router.get("/test-db")
async def test_database(db: AsyncSession = Depends(get_db)):
    """Test database connection"""
    try:
        # Simple query to test connection
        result = await db.execute(select(1))
        return {"status": "Database connected", "result": result.scalar()}
    except Exception as e:
        return {"status": "Database error", "error": str(e)}
```

**8. Update main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.api import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Close connections
    await engine.dispose()

# Create FastAPI instance
app = FastAPI(
    title="Invoice Parser API",
    description="AI-powered invoice data extraction",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)

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
```

**9. Create .env file:**
```env
DATABASE_URL=postgresql+asyncpg://username:password@host/database
SECRET_KEY=your-secret-key-here
```

#### Testing This Step

**1. Test Database Connection:**
```bash
curl http://localhost:8000/api/users/test-db
```

**2. Create a User:**
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "securepassword123"
  }'
```

**3. Test Duplicate Prevention:**
Run the same create user command again - should get error

#### Common Issues & Solutions

**Issue: Connection Refused**
```
asyncpg.exceptions.ConnectionDoesNotExistError
```
**Solution:** Check DATABASE_URL format and Neon dashboard

**Issue: Table Already Exists**
```
sqlalchemy.exc.ProgrammingError: relation "users" already exists
```
**Solution:** This is fine - tables already created

**Issue: Import Errors**
```
ModuleNotFoundError: No module named 'app'
```
**Solution:** Run from backend directory with correct PYTHONPATH

#### Checklist Before Next Step
- [ ] Database connects successfully
- [ ] Can create users
- [ ] Duplicate prevention works
- [ ] Password is hashed (check in logs)
- [ ] Models and schemas organized
</lesson>

### STEP-005 through STEP-010

[Due to length constraints, I'll summarize the remaining steps structure. Each would follow the same detailed pattern:]

### STEP-005: User Authentication
- JWT token generation and validation
- Login/logout endpoints
- Protected routes
- Frontend auth context

### STEP-006: File Upload System
- Multer-style file handling in FastAPI
- File validation and security
- User-isolated storage
- Frontend upload component

### STEP-007: AI Integration - Gemini API
- LangChain setup
- Structured output parsing
- Error handling and retries
- Mock AI for testing

### STEP-008: Complete Invoice Processing
- Complex database relationships
- Transaction handling
- Data validation pipeline
- Results display

### STEP-009: Dashboard & Analytics
- Statistics aggregation
- Pagination implementation
- Search and filtering
- Chart visualizations

### STEP-010: Polish & Production Ready
- Comprehensive error handling
- Logging and monitoring
- Performance optimization
- Deployment preparation

## Architecture Decisions Log

```yaml
decisions:
  - decision_id: "DEC-001"
    step: 1
    choice: "Start with FastAPI instead of frontend"
    reasoning: "Backend is the foundation; easier to test API-first"
    alternatives_considered: ["Start with React", "Build both simultaneously"]

  - decision_id: "DEC-002"
    step: 2
    choice: "Use Vite over Create React App"
    reasoning: "Faster development, better for learning modern tools"
    alternatives_considered: ["CRA", "Next.js", "Plain webpack"]

  - decision_id: "DEC-003"
    step: 3
    choice: "Implement dark mode early"
    reasoning: "Easier to add styles with dark mode in mind from start"
    alternatives_considered: ["Add dark mode last", "Skip dark mode"]

  - decision_id: "DEC-004"
    step: 4
    choice: "Use Neon PostgreSQL"
    reasoning: "Free tier, easy setup, good for learning"
    alternatives_considered: ["Local PostgreSQL", "SQLite", "Supabase"]

  - decision_id: "DEC-005"
    step: 5
    choice: "JWT over sessions"
    reasoning: "Stateless, industry standard, good for APIs"
    alternatives_considered: ["Session cookies", "OAuth only"]
```

## Testing Framework

### After Each Step Testing Protocol

```javascript
// Automated Testing with Playwright MCP
async function testStep(stepNumber) {
  // Start services
  await Bash({
    command: "cd backend && uvicorn app.main:app --reload",
    run_in_background: true
  });

  await Bash({
    command: "cd frontend && npm run dev",
    run_in_background: true
  });

  // Wait for services
  await Bash({ command: "sleep 5" });

  // Test backend
  const apiTest = await Bash({
    command: "curl http://localhost:8000/health"
  });

  // Test frontend
  await browser_navigate({ url: "http://localhost:5173" });
  await browser_wait_for({ text: "Invoice Parser AI" });

  // Take screenshot
  await browser_take_screenshot({
    filename: `step-${stepNumber}-complete.png`,
    fullPage: true
  });

  // Verify previous functionality
  if (stepNumber > 1) {
    await runRegressionTests(stepNumber - 1);
  }

  // Close browser
  await browser_close();
}
```

## Commands Reference

```bash
# Backend Development
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend Development
cd frontend
npm install
npm run dev
npm run build

# Database
# Use Neon dashboard for database management

# Testing
pytest backend/tests/
npm test frontend/

# Git Workflow
git add .
git commit -m "STEP-XXX: Description"
git push
```

## Continuous Update Protocol

After EVERY step completion:
1. Update step YAML status to "completed"
2. Add detailed implementation_notes
3. Document any learner_feedback
4. Test all previous steps still work
5. Take screenshots for documentation
6. Commit with message: "STEP-{id}: {description}"

## Emergency Recovery

If something breaks:
1. Check error messages carefully
2. Verify all services are running
3. Check environment variables
4. Clear browser cache
5. Restart all services
6. Check previous step's working code
7. Refer to implementation_notes

## Learning Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Tailwind: https://tailwindcss.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Neon: https://neon.tech/docs

### Common Patterns
- API-first development
- Component-based UI
- Service layer architecture
- Async programming
- JWT authentication

## Final Project Structure

```
invoice-parser/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── uploads/
│   ├── tests/
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── App.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Success Metrics

By the end of this course, learners will:
1. ✅ Build a full-stack application from scratch
2. ✅ Integrate AI APIs for real functionality
3. ✅ Implement secure authentication
4. ✅ Handle file uploads safely
5. ✅ Work with modern databases
6. ✅ Create responsive, themed UIs
7. ✅ Understand production patterns
8. ✅ Debug and troubleshoot effectively

## Notes for Instructors

1. **Pace**: Let learners fully complete each step
2. **Debugging**: Teach problem-solving, not just solutions
3. **Code Quality**: Emphasize clean, readable code
4. **Testing**: Make testing a habit, not an afterthought
5. **Documentation**: Update this plan with discoveries

---

*This is a living document. Update it continuously as you teach and learn.*