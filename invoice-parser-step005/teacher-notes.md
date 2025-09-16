# STEP-005: JWT User Authentication - Teacher Notes

## Overview
In this step, students implement JWT (JSON Web Token) based authentication for the invoice parser application. This builds on the user management system from STEP-004 by adding secure token-based authentication.

## Learning Objectives
- Understand JWT tokens and their structure
- Implement OAuth2 password flow
- Create authentication endpoints
- Protect routes with authentication dependencies
- Handle token verification and user sessions

## Key Concepts

### 1. JWT Tokens
- **What**: JSON Web Tokens are a secure way to transmit information between parties
- **Structure**: Header.Payload.Signature
- **Benefits**: Stateless, scalable, cross-domain support
- **Use Case**: API authentication without server-side sessions

### 2. OAuth2 Password Flow
- Standard authentication flow for username/password
- Returns a bearer token for subsequent requests
- Token included in Authorization header

### 3. Authentication Dependencies
- FastAPI dependency injection for route protection
- Automatic token extraction and verification
- User object injection into protected routes

## Implementation Checklist

### Backend Changes

#### 1. Install Dependencies
```bash
pip install python-jose[cryptography] python-multipart
```

#### 2. Security Module (`app/core/security.py`)
- ✅ Password hashing functions (from STEP-004)
- ✅ Token creation function
- ✅ Token verification function
- ✅ Configuration for algorithm and expiration

#### 3. Authentication Schemas (`app/schemas/auth.py`)
- ✅ Token response model
- ✅ Token data model
- ✅ Login request model

#### 4. Dependencies Module (`app/core/dependencies.py`)
- ✅ OAuth2PasswordBearer scheme
- ✅ get_current_user dependency
- ✅ get_current_active_user dependency
- ✅ Token verification logic

#### 5. Auth API Routes (`app/api/auth.py`)
- ✅ POST /api/auth/register - User registration
- ✅ POST /api/auth/login - User login (OAuth2 compatible)
- ✅ GET /api/auth/me - Get current user

#### 6. Protected Routes
- ✅ Update user routes to require authentication
- ✅ Add authorization logic (users can only update own profile)

## Common Student Challenges

### 1. Token Format Issues
**Problem**: Students forget OAuth2PasswordRequestForm expects form data, not JSON
**Solution**:
```python
# Wrong - JSON body
response = requests.post("/login", json={"username": "test", "password": "pass"})

# Correct - Form data
response = requests.post("/login", data={"username": "test", "password": "pass"})
```

### 2. Username vs Email Confusion
**Problem**: OAuth2 spec uses "username" field, but we want to support email login
**Solution**: Modified authenticate_user to accept either:
```python
async def authenticate_user(db: AsyncSession, username_or_email: str, password: str):
    user = await UserService.get_user_by_email(db, username_or_email)
    if not user:
        user = await UserService.get_user_by_username(db, username_or_email)
```

### 3. Missing SECRET_KEY
**Problem**: JWT encoding requires a secret key
**Solution**: Ensure .env file has:
```
SECRET_KEY=your-secret-key-here-change-in-production
```

### 4. Token in Headers
**Problem**: Students forget to include token in protected route requests
**Solution**: Always include Authorization header:
```python
headers = {"Authorization": f"Bearer {token}"}
```

## Testing Guide

### Manual Testing with curl

1. **Register a new user**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"SecurePass123!"}'
```

2. **Login to get token**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -F "username=test@example.com" \
  -F "password=SecurePass123!"
```

3. **Access protected route**:
```bash
TOKEN="your-token-here"
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Automated Testing
Use the provided `test_auth.py` script which tests:
- User registration
- Login and token generation
- Accessing protected routes with token
- Unauthorized access rejection

## Security Best Practices

### 1. Secret Key Management
- Never commit SECRET_KEY to version control
- Use strong, random secret keys in production
- Rotate keys periodically

### 2. Token Expiration
- Keep token expiration reasonable (30 minutes default)
- Implement refresh tokens for production
- Clear tokens on logout (frontend)

### 3. Password Requirements
- Enforce minimum password length
- Consider adding password complexity rules
- Never log passwords (even hashed)

### 4. HTTPS in Production
- Always use HTTPS in production
- Tokens can be intercepted over HTTP
- Consider additional security headers

## Extension Activities

### 1. Refresh Tokens
Implement refresh token flow:
- Longer-lived refresh tokens
- Short-lived access tokens
- Token refresh endpoint

### 2. Role-Based Access Control
Add user roles:
- Admin, Manager, User roles
- Role-based route protection
- Permission decorators

### 3. Social Login
Integrate OAuth2 providers:
- Google login
- GitHub login
- Facebook login

### 4. Two-Factor Authentication
Add 2FA support:
- TOTP implementation
- SMS verification
- Email verification

## Debugging Tips

### 1. Token Decode Errors
Check token with jwt.io debugger to see:
- Proper structure
- Expiration time
- Payload contents

### 2. 401 Unauthorized
Common causes:
- Token expired
- Wrong secret key
- Malformed token
- Missing Bearer prefix

### 3. 422 Unprocessable Entity
Usually means:
- Wrong content type (use form data for login)
- Missing required fields
- Type validation errors

## Assessment Criteria

### Functional Requirements (70%)
- [ ] Registration endpoint works
- [ ] Login returns valid JWT token
- [ ] Protected routes require authentication
- [ ] Token verification works correctly
- [ ] User can access own profile

### Code Quality (20%)
- [ ] Proper error handling
- [ ] Clean separation of concerns
- [ ] Consistent code style
- [ ] No hardcoded secrets

### Security (10%)
- [ ] Passwords properly hashed
- [ ] Tokens expire appropriately
- [ ] Authorization logic correct
- [ ] No sensitive data in responses

## Next Steps
After completing authentication, students will:
1. STEP-006: Build invoice upload functionality
2. STEP-007: Integrate AI for data extraction
3. STEP-008: Create frontend authentication UI

## Resources
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - JWT debugger
- [OAuth2 Specification](https://oauth.net/2/)
- [Python-JOSE Documentation](https://python-jose.readthedocs.io/)

## Troubleshooting Checklist
- [ ] Virtual environment activated?
- [ ] All dependencies installed?
- [ ] Database migrations run?
- [ ] SECRET_KEY in .env file?
- [ ] Server running on correct port?
- [ ] Using correct content-type for login?
- [ ] Token included in Authorization header?
- [ ] Token not expired?

## Sample Solution Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py          # ✨ NEW: Auth endpoints
│   │   └── users.py         # 🔐 UPDATED: Protected routes
│   ├── core/
│   │   ├── dependencies.py  # ✨ NEW: Auth dependencies
│   │   └── security.py      # 📝 UPDATED: JWT functions
│   ├── schemas/
│   │   └── auth.py          # ✨ NEW: Auth schemas
│   └── services/
│       └── user_service.py  # 📝 UPDATED: authenticate_user
└── test_auth.py             # ✨ NEW: Test script
```

This completes the JWT authentication implementation!