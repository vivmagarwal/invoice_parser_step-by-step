# STEP-003: Tailwind CSS and Dark Mode

## What You'll Build
Transform the React app from basic CSS to modern Tailwind utilities with dark mode support.

## Directory Structure
```
invoice-parser-step003/
├── starting-code/      # React + FastAPI from STEP-002
├── ending-code/        # App with Tailwind and dark mode
│   ├── backend/       # FastAPI (unchanged from STEP-002)
│   └── frontend/      # React with Tailwind CSS
├── teacher-notes.md   # Detailed implementation guide
└── README.md         # This file
```

## Quick Start

### Run the Application
**Terminal 1 - Backend:**
```bash
cd ending-code/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd ending-code/frontend
npm install
npm run dev
```

### Test Features
1. Visit http://localhost:5173
2. Click moon/sun icon to toggle dark mode
3. Refresh page - theme persists
4. Resize window - responsive design works

## Key Changes from STEP-002
- ✅ Tailwind CSS replaces traditional CSS
- ✅ Dark mode with theme toggle
- ✅ Theme Context for global state
- ✅ LocalStorage for persistence
- ✅ Responsive grid layout
- ✅ Modern UI with gradients and shadows

## Learning Objectives
- Utility-first CSS approach
- React Context API
- Dark mode implementation
- Responsive design with Tailwind
- State persistence with localStorage

## Tech Stack
- **Frontend**: React 18, Vite, Tailwind CSS 3
- **Backend**: FastAPI (unchanged)
- **Styling**: Tailwind utilities
- **State**: React Context API

## What's New

### Files Added
```
frontend/
├── src/
│   └── contexts/
│       └── ThemeContext.jsx  # Theme management
├── tailwind.config.js        # Tailwind configuration
└── postcss.config.js         # PostCSS configuration
```

### Files Modified
- `src/index.css` - Replaced with Tailwind directives
- `src/App.jsx` - Rewritten with Tailwind classes
- `src/main.jsx` - Added ThemeProvider wrapper

### Files Removed
- `src/App.css` - No longer needed with Tailwind

## Common Commands
```bash
# Frontend development
npm run dev           # Start dev server
npm run build        # Production build
npm run preview      # Preview production build

# Backend development
uvicorn app.main:app --reload

# Tailwind
npx tailwindcss init -p  # Initialize configs
```

## Testing Checklist
- [ ] App loads with styled interface
- [ ] Dark mode toggle works
- [ ] Theme persists on refresh
- [ ] API connection maintained
- [ ] Responsive on mobile
- [ ] No console errors

## Next Step
STEP-004 will add PostgreSQL database with SQLAlchemy models for user management.

## For Teachers
See `teacher-notes.md` for:
- Complete implementation guide
- Common issues and solutions
- Assessment points
- Extension activities
- Time management tips