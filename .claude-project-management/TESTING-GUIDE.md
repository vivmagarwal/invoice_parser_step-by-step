# Comprehensive Testing Guide for Full-Stack Applications

## Overview
This guide is based on real-world testing experience with the Invoice Parser application and provides a systematic approach to testing full-stack applications.

## Pre-Testing Setup Checklist

### 1. Environment Variables
```bash
# Check .env file exists and has all required keys
cat .env

# Required for Invoice Parser:
GOOGLE_API_KEY=<valid_api_key>
DATABASE_URL=<connection_string>
JWT_SECRET_KEY=<secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Database Connection Testing
Always test database connections independently FIRST:

```python
# Create test-db.py
import psycopg2  # or your database driver

DATABASE_URL = "your_connection_string"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connected successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### 3. Directory Structure
Ensure all required directories exist:
```bash
mkdir -p static uploads
```

## Testing Workflow

### Phase 1: Backend Testing

1. **Start Backend Server**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Verify Health Check**
```bash
curl http://localhost:8000/api/health
# Should return database status
```

3. **Check API Documentation**
- Navigate to http://localhost:8000/docs
- Verify all endpoints are listed

### Phase 2: Frontend Testing

1. **Start Frontend**
```bash
cd frontend
npm install
npm run dev
```

2. **Initial Load Test**
- Check console for errors
- Verify API connection status
- Check for CORS issues

### Phase 3: Integration Testing with Playwright

1. **User Registration Flow**
```javascript
// Test user creation
await page.goto('http://localhost:5173')
await page.click('Register')
await page.fill('email', 'test@example.com')
await page.fill('password', 'securepassword')
await page.click('Submit')
```

2. **Authentication Testing**
- Verify JWT token storage
- Test protected routes
- Check session persistence

3. **Core Functionality Testing**
- File uploads
- AI processing
- Database operations
- Real-time updates

### Phase 4: Mobile Responsive Testing

```javascript
// Set mobile viewport
await page.setViewportSize({ width: 390, height: 844 })
// Take screenshot
await page.screenshot({ path: 'mobile-view.png' })
```

## Common Issues and Solutions

### Issue 1: Database Connection Failures
**Symptoms**:
- "password authentication failed"
- "connection refused"

**Solutions**:
1. Verify connection string format
2. Check if using pooler vs direct connection (Neon specific)
3. Test with standalone script first
4. Ensure SSL mode is correct

### Issue 2: API Key Expiration
**Symptoms**:
- "API_KEY_INVALID"
- "401 Unauthorized"

**Solutions**:
1. Generate new API key from provider
2. Update .env file
3. Restart backend server to load new env vars

### Issue 3: Missing Directories
**Symptoms**:
- "Directory 'static' does not exist"
- File upload failures

**Solutions**:
```bash
mkdir -p static uploads
chmod 755 static uploads
```

### Issue 4: CORS Errors
**Symptoms**:
- "CORS policy" errors in browser console
- API calls blocked

**Solutions**:
1. Check backend CORS configuration
2. Ensure frontend proxy is set correctly
3. Verify allowed origins match

## Testing Documentation Template

### TEST_REPORT.md Structure
```markdown
# Application Test Report

## Test Date: YYYY-MM-DD

## Executive Summary
[Overall status and key findings]

## Test Environment
- Backend: [Framework and port]
- Frontend: [Framework and port]
- Database: [Type and location]
- External Services: [APIs used]

## Test Results Summary
| Feature | Status | Notes |
|---------|--------|-------|
| Feature 1 | ✅/❌ | Details |

## Detailed Test Results
[Comprehensive test details]

## Issues Found and Fixed
[List all issues and solutions]

## Recommendations
[Future improvements]
```

## Automated Testing with TodoWrite

Use TodoWrite to track testing progress:

```javascript
const testTasks = [
  "Test user registration flow",
  "Test user login flow",
  "Test file upload functionality",
  "Test AI processing",
  "Test database operations",
  "Test dashboard statistics",
  "Test responsive design",
  "Document findings"
]
```

## Performance Testing Checklist

- [ ] Page load time < 3 seconds
- [ ] API response time < 2 seconds
- [ ] Memory usage stable over time
- [ ] No memory leaks in React components
- [ ] Database queries optimized
- [ ] Image loading optimized

## Security Testing Checklist

- [ ] Passwords hashed (never plain text)
- [ ] JWT tokens expire appropriately
- [ ] API keys not exposed in frontend
- [ ] SQL injection prevention
- [ ] XSS protection enabled
- [ ] HTTPS in production
- [ ] Rate limiting implemented

## Best Practices

1. **Always Test in Order**: Backend → Database → Frontend
2. **Document Everything**: Failures are as important as successes
3. **Use Real Data**: Test with actual files/inputs when possible
4. **Test Edge Cases**: Empty inputs, large files, special characters
5. **Verify Cleanup**: Ensure test data doesn't pollute production

## Testing Tools Recommendation

1. **Backend Testing**:
   - Postman/Thunder Client for API testing
   - pytest for unit tests
   - locust for load testing

2. **Frontend Testing**:
   - Playwright for E2E testing
   - React Testing Library for components
   - Lighthouse for performance

3. **Database Testing**:
   - Standalone connection scripts
   - pgAdmin/TablePlus for visualization
   - Query performance analyzers

## Continuous Testing Strategy

1. **Before Each Session**:
   - Verify environment variables
   - Check database connectivity
   - Ensure all services are running

2. **After Major Changes**:
   - Run full test suite
   - Update TEST_REPORT.md
   - Document any new issues

3. **Before Deployment**:
   - Full regression testing
   - Security audit
   - Performance benchmarking

## Lessons Learned from Invoice Parser Testing

1. **Database credentials often change** - Always verify first
2. **API keys expire frequently** - Keep backups ready
3. **Directory creation is often missed** - Include in setup scripts
4. **Test with real data early** - Synthetic data hides issues
5. **Document fixes immediately** - You'll forget the solution later

---

*This guide is a living document. Update it with new learnings from each testing session.*