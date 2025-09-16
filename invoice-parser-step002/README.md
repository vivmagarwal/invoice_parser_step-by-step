# STEP-002: React Frontend with Vite

## Directory Structure
```
invoice-parser-step002/
├── starting-code/      # Working FastAPI backend from STEP-001
├── ending-code/        # Backend + React frontend application
│   ├── backend/       # FastAPI server (unchanged from STEP-001)
│   └── frontend/      # New React application
├── teacher-notes.md   # Detailed teaching guide with run instructions
└── README.md         # This file
```

## Quick Start (for Teachers/Testing)

### Terminal 1: Backend
```bash
cd ending-code/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd ending-code/frontend
npm install
npm run dev
```

### Test the Application
1. Open http://localhost:5173 in browser
2. Should see "Invoice Parser AI" interface
3. API connection status should show "✓ Connected to API"
4. Click "Refresh" button to test API calls

## For Detailed Instructions
See `teacher-notes.md` for:
- Complete setup and run instructions
- Manual testing for all features
- Expected outputs
- Common issues and solutions
- Teaching guidance

## Learning Objectives
- Set up React with Vite
- Understand React hooks (useState, useEffect)
- Implement async API calls
- Handle loading and error states
- Build responsive UI

## What Students Build
Starting from a working backend, students add:
- React frontend application
- API integration with axios
- Loading and error states
- Responsive UI with modern CSS
- Full-stack connection

## Key Technologies
- React 18 with hooks
- Vite for fast development
- Axios for API calls
- Modern CSS for styling
- CORS configuration