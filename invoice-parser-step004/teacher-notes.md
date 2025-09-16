# Teacher Notes - STEP 004: PostgreSQL Database Setup

## Overview
This step introduces database integration using SQLAlchemy ORM with async support. We implement a User model with complete CRUD operations, password hashing for security, and RESTful API endpoints.

## Learning Objectives
1. Understanding SQLAlchemy ORM with async/await
2. Implementing secure password hashing
3. Creating Pydantic schemas for data validation
4. Building RESTful CRUD operations
5. Database connection management
6. Dependency injection in FastAPI

## Key Concepts Covered

### 1. Database Configuration
- **SQLAlchemy Async Engine**: Using `create_async_engine` for non-blocking database operations
- **Connection String**: SQLite with aiosqlite driver for simplicity (easily switchable to PostgreSQL)
- **Session Management**: Using `async_sessionmaker` for database sessions

### 2. ORM Models
- **Declarative Base**: Creating models that inherit from `Base`
- **Column Types**: Integer, String, Boolean, DateTime
- **Indexes**: Unique constraints on email and username
- **Timestamps**: Server-side defaults for created_at

### 3. Pydantic Schemas
- **Inheritance Pattern**: Base -> Create/Update -> Response models
- **EmailStr**: Built-in email validation
- **Optional Fields**: Using `Optional[Type]` for nullable fields
- **Config Classes**: `from_attributes = True` for ORM compatibility

### 4. Security
- **Password Hashing**: Using passlib with bcrypt
- **Never Store Plain Passwords**: Always hash before storing
- **Verification**: Comparing hashed passwords securely

### 5. Service Layer Pattern
- **Separation of Concerns**: Business logic separate from API routes
- **Reusable Functions**: CRUD operations in service class
- **Error Handling**: Proper exception handling for duplicates

### 6. API Design
- **RESTful Endpoints**: Standard HTTP methods (GET, POST, PUT, DELETE)
- **Dependency Injection**: Using `Depends(get_db)` for database sessions
- **Proper Status Codes**: 200, 201, 400, 404, etc.
- **Response Models**: Consistent API responses

## Common Issues and Solutions

### Issue 1: Missing Dependencies
**Problem**: ModuleNotFoundError for greenlet or email-validator
**Solution**: These are required dependencies for SQLAlchemy and Pydantic EmailStr
```bash
pip install greenlet email-validator
```

### Issue 2: Database File Location
**Problem**: SQLite database created in wrong location
**Solution**: Database is created relative to where you run the server. Always run from backend directory.

### Issue 3: Async Context Errors
**Problem**: "ValueError: the greenlet library is required"
**Solution**: Install greenlet package - it's required for SQLAlchemy's async support

## Testing Instructions

### 1. Environment Setup
```bash
cd invoice-parser-step004/ending-code/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
uvicorn app.main:app --reload --port 8004
```
You should see:
- Database tables being created
- Server running on http://127.0.0.1:8004

### 3. Test User Creation
```bash
curl -X POST http://localhost:8004/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "password": "SecurePassword123"
  }'
```

Expected Response:
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-09-16T10:52:12"
}
```

### 4. Test Getting All Users
```bash
curl http://localhost:8004/api/users/
```

### 5. Test Getting Single User
```bash
curl http://localhost:8004/api/users/1
```

### 6. Test Updating User
```bash
curl -X PUT http://localhost:8004/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith"
  }'
```

### 7. Test Deleting User
```bash
curl -X DELETE http://localhost:8004/api/users/1
```

### 8. Test Duplicate Prevention
Try creating another user with same email:
```bash
curl -X POST http://localhost:8004/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "different",
    "password": "password"
  }'
```
Should return 400 error: "User with this email or username already exists"

### 9. Check API Documentation
Visit: http://localhost:8004/docs
- Interactive Swagger UI documentation
- Try all endpoints directly from browser

### 10. Verify Database File
```bash
ls -la *.db
```
You should see `invoice_parser.db` file created

## Code Structure Explanation

### Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app with lifespan events
│   ├── api/
│   │   ├── __init__.py
│   │   └── users.py      # User API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py     # Settings configuration
│   │   ├── database.py   # Database engine and session
│   │   └── security.py   # Password hashing utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py       # SQLAlchemy User model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py       # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── user_service.py  # Business logic
├── requirements.txt       # Python dependencies
├── venv/                  # Virtual environment
└── invoice_parser.db      # SQLite database file
```

### Key Files Explained

1. **app/core/config.py**: Centralized configuration using pydantic-settings
2. **app/core/database.py**: Database connection and session management
3. **app/models/user.py**: SQLAlchemy ORM model definition
4. **app/schemas/user.py**: Pydantic models for validation
5. **app/services/user_service.py**: Business logic layer
6. **app/api/users.py**: HTTP endpoint handlers

## Best Practices Demonstrated

1. **Async/Await Throughout**: Non-blocking database operations
2. **Dependency Injection**: Clean session management
3. **Service Layer**: Separation of business logic
4. **Proper Error Handling**: Try/except with meaningful messages
5. **Security First**: Password hashing, no plain text storage
6. **Type Hints**: Full type annotations for better IDE support
7. **Modular Structure**: Clean separation of concerns

## Extension Ideas for Students

1. **Add Email Verification**: Implement email confirmation flow
2. **Add JWT Authentication**: Create login endpoint with tokens
3. **Add Role-Based Access**: Implement admin vs regular users
4. **Add Pagination**: Implement limit/offset for user listing
5. **Add Search/Filter**: Search users by name or email
6. **Switch to PostgreSQL**: Change connection string to use real PostgreSQL
7. **Add User Profile**: Extend model with profile picture, bio, etc.
8. **Add Audit Logs**: Track who changed what and when

## Troubleshooting Guide

### Server Won't Start
1. Check virtual environment is activated
2. Verify all dependencies installed
3. Check no other service on port 8004
4. Look for import errors in terminal

### Database Errors
1. Delete `invoice_parser.db` and restart to recreate
2. Check SQLite is installed on system
3. Verify write permissions in directory

### API Returns 422 Unprocessable Entity
1. Check request body JSON is valid
2. Verify all required fields present
3. Check email format is valid
4. Review Pydantic validation errors in response

### Password Not Working
1. Ensure bcrypt is installed
2. Check password meets requirements
3. Verify hashing function is called

## Summary
This step transforms our application from a simple API to a full-featured backend with:
- Persistent data storage
- User management system
- Secure password handling
- Professional API structure
- Scalable architecture

Students should understand:
- How ORMs abstract database operations
- Importance of data validation
- Security best practices
- RESTful API design principles
- Async programming benefits

The foundation is now ready for authentication (JWT tokens) and business logic (invoice processing) in upcoming steps.