# STEP-002: React Frontend with Vite - Teacher Notes

## Overview
This step introduces students to React with Vite, creating a frontend that connects to our FastAPI backend. Students learn modern React hooks, async data fetching, and how to build a responsive UI.

## Learning Objectives
1. Set up a React application using Vite
2. Understand React hooks (useState, useEffect)
3. Implement async API calls with axios
4. Handle loading states and errors
5. Create a responsive UI with modern CSS

## Starting Point
- **starting-code/**: Contains the working FastAPI backend from STEP-001
- Students have a working API with three endpoints
- Backend is tested and functional

## Ending Point
- **ending-code/**: Full stack application with:
  - Backend (unchanged from STEP-001)
  - Frontend React app that connects to the API
  - Responsive UI showing API connection status
  - Error handling and loading states

## Step-by-Step Instructions to Run and Test ending-code

### Setup Instructions

#### Terminal 1: Backend Setup
1. **Navigate to backend directory**:
   ```bash
   cd invoice-parser-step002/ending-code/backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install backend dependencies**:
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
   INFO: Started reloader process [####]
   INFO: Started server process [####]
   INFO: Waiting for application startup.
   INFO: Application startup complete.
   ```

#### Terminal 2: Frontend Setup
1. **Navigate to frontend directory**:
   ```bash
   cd invoice-parser-step002/ending-code/frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Start the React development server**:
   ```bash
   npm run dev
   ```

   Expected output:
   ```
   VITE v5.x.x ready in xxx ms

   ➜ Local:   http://localhost:5173/
   ➜ Network: use --host to expose
   ➜ press h + enter to show help
   ```

### Manual Testing Instructions

#### Test 1: Backend API Endpoints
1. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/
   ```
   Expected: Welcome message JSON

2. **Test health endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: Health status JSON

3. **Test API endpoint**:
   ```bash
   curl http://localhost:8000/api/test
   ```
   Expected: API test data with supported formats

#### Test 2: Frontend Application
1. **Open browser**:
   - Navigate to http://localhost:5173/

2. **Initial load**:
   - Should see "Invoice Parser AI" header
   - Loading indicator should appear briefly
   - API connection status should show "✓ Connected to API"
   - Should display "API is working!" message
   - Features section should list supported formats

3. **Test refresh button**:
   - Click the "Refresh" button
   - Should see loading state briefly
   - Data should reload successfully

#### Test 3: Error Handling
1. **Stop the backend server** (Ctrl+C in Terminal 1)

2. **Click Refresh in frontend**:
   - Should see error message: "Failed to connect to API"
   - Error should be in red text

3. **Restart backend** and click Refresh:
   - Connection should restore
   - Success message should reappear

#### Test 4: Browser Console
1. **Open Developer Tools** (F12)
2. **Check Console tab**:
   - Should see no errors when connected
   - Should see "API Error:" logs when backend is down

### Verification Checklist
- [ ] Backend server starts on port 8000
- [ ] All backend endpoints return correct JSON
- [ ] Frontend server starts on port 5173
- [ ] Frontend loads without errors
- [ ] API connection successful on page load
- [ ] Loading states display correctly
- [ ] Error handling works when backend is down
- [ ] Refresh button fetches new data
- [ ] UI is responsive and styled correctly
- [ ] No CORS errors in console

### Troubleshooting Common Issues

#### Issue 1: CORS Error
**Symptom**: "Access to XMLHttpRequest blocked by CORS policy"
**Solution**:
- Verify backend CORS middleware includes `http://localhost:5173`
- Ensure backend is running on port 8000
- Check axios is calling `http://localhost:8000/api/test`

#### Issue 2: Cannot find module 'axios'
**Symptom**: Module not found error
**Solution**:
```bash
npm install axios
```

#### Issue 3: Port Already in Use
**Symptom**: "Port 5173 is already in use"
**Solution**:
- Kill existing process or use different port
- Update vite.config.js to use different port

#### Issue 4: Backend Connection Failed
**Symptom**: "Failed to connect to API" message
**Solution**:
- Ensure backend is running on port 8000
- Check no firewall blocking connections
- Verify URL in App.jsx is correct

## Key Teaching Points

### 1. React Hooks
Explain the modern approach:
- `useState`: Manages component state
- `useEffect`: Handles side effects (API calls)
- Hooks replace class components
- Rules of hooks (only at top level)

### 2. Async Data Fetching
- Promise-based with async/await
- Try-catch for error handling
- Loading states for better UX
- When to fetch data (useEffect with empty deps)

### 3. Vite Benefits
- Fast hot module replacement (HMR)
- Modern build tool replacing Create React App
- Built-in proxy configuration
- Optimized production builds

### 4. Component Structure
- Functional components only
- JSX syntax and expressions
- Conditional rendering patterns
- Event handling (onClick)

## Common Student Issues

### Issue 1: useEffect Running Multiple Times
**Symptom**: API called twice on load
**Explanation**: React StrictMode in development
**Solution**: This is normal in dev, won't happen in production

### Issue 2: State Not Updating
**Symptom**: UI doesn't reflect state changes
**Solution**: Ensure using setState correctly, not mutating state

### Issue 3: Async Without Await
**Symptom**: Data is undefined
**Solution**: Always use await with async functions

## Demonstration Flow

1. **Show the End Goal**:
   - Demo working full-stack app
   - Show API connection in action
   - Demonstrate error handling

2. **Build Step by Step**:
   - Create React app with Vite
   - Install and configure axios
   - Build component structure
   - Add styling
   - Test with backend

3. **Debugging Session**:
   - Intentionally stop backend
   - Show error handling
   - Use browser DevTools

4. **Let Students Explore**:
   - Add a new API endpoint
   - Modify the UI styling
   - Add additional state

## Assessment Checkpoints
✅ Both servers run without errors
✅ Frontend successfully connects to backend
✅ Loading and error states work correctly
✅ Student can explain useState and useEffect
✅ Student can add a new API call

## Extensions for Advanced Students
- Add a form to send POST requests
- Implement a dark mode toggle
- Add animations with CSS transitions
- Create additional React components
- Add TypeScript support

## Connection to Next Step
The ending-code of this step becomes the starting-code for STEP-003. Students will:
- Add database connectivity
- Implement user models
- Create registration and login functionality

## Time Management
- 20 min: Explain React concepts and Vite
- 45 min: Build frontend together
- 30 min: Students practice and modify
- 15 min: Debug common issues
- 10 min: Demonstrate full-stack connection

## Key Vocabulary
- **Component**: Reusable UI building block
- **Props**: Data passed to components
- **State**: Component's internal data
- **Hook**: Function that adds React features
- **JSX**: JavaScript XML syntax
- **HMR**: Hot Module Replacement

## Success Metrics
Students successfully complete this step when they:
1. Have both backend and frontend running
2. Frontend connects to all three API endpoints
3. Can handle loading and error states
4. Understand React hooks basics
5. Can modify and extend the frontend