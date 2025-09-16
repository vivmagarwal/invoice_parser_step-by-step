# STEP-006: File Upload System - Teacher Notes

## Overview
In this step, students implement a secure file upload system with validation, storage, and database tracking. This is essential for the invoice parser as users need to upload invoice files before AI processing.

## Learning Objectives
- Implement secure file uploads with FastAPI
- Validate file types and sizes
- Organize file storage on disk
- Track file metadata in database
- Handle file operations asynchronously
- Implement proper error handling

## Key Concepts

### 1. Multipart Form Data
- **What**: HTTP protocol for uploading files
- **FastAPI Support**: Built-in with `UploadFile` class
- **Requirements**: python-multipart package
- **Content Type**: multipart/form-data (not JSON)

### 2. File Validation
- **Type Checking**: Verify file extensions and MIME types
- **Size Limits**: Prevent excessive storage usage
- **Security**: Prevent malicious file uploads
- **User Feedback**: Clear error messages

### 3. File Storage Strategy
- **User Isolation**: Separate directories per user
- **Unique Names**: UUID-based filenames prevent conflicts
- **Original Names**: Preserve for user reference
- **Path Management**: Systematic directory structure

### 4. Asynchronous File Operations
- **aiofiles**: Async file I/O library
- **Chunked Reading**: Memory-efficient for large files
- **Error Handling**: Cleanup on failure

## Implementation Checklist

### Backend Changes

#### 1. Install Dependencies
```bash
pip install aiofiles Pillow
```

#### 2. Invoice Model (`app/models/invoice.py`)
- ✅ File metadata fields
- ✅ Processing status enum
- ✅ Extracted data fields (for future AI processing)
- ✅ User relationship
- ✅ Timestamps

#### 3. File Service (`app/services/file_service.py`)
- ✅ File validation logic
- ✅ Safe file storage with UUID names
- ✅ User-specific directories
- ✅ File size checking during upload
- ✅ File deletion support

#### 4. Invoice Service (`app/services/invoice_service.py`)
- ✅ CRUD operations for invoice records
- ✅ User filtering for security
- ✅ Pagination support

#### 5. API Endpoints (`app/api/invoices.py`)
- ✅ POST /api/invoices/upload - Upload invoice file
- ✅ GET /api/invoices/ - List user's invoices
- ✅ GET /api/invoices/{id} - Get specific invoice
- ✅ DELETE /api/invoices/{id} - Delete invoice

#### 6. Database Updates
- ✅ User model updated with invoice relationship
- ✅ Invoice table created on startup
- ✅ Cascade delete configured

## Common Student Challenges

### 1. Form Data vs JSON
**Problem**: Students try to send files as JSON
**Solution**:
```python
# Wrong - JSON body
response = requests.post("/upload", json={"file": file_content})

# Correct - Multipart form data
files = {"file": (filename, file_object, mime_type)}
response = requests.post("/upload", files=files)
```

### 2. File Size Handling
**Problem**: Server crashes with large files
**Solution**: Check size during chunked reading:
```python
while content := await file.read(8192):
    file_size += len(content)
    if file_size > MAX_FILE_SIZE:
        # Clean up and raise error
```

### 3. Missing Upload Directory
**Problem**: FileNotFoundError when saving files
**Solution**: Create directories with parents:
```python
user_dir = cls.UPLOAD_DIR / str(user_id)
user_dir.mkdir(parents=True, exist_ok=True)
```

### 4. File Cleanup on Error
**Problem**: Partial files left on disk after errors
**Solution**: Always clean up in exception handlers:
```python
except Exception as e:
    if file_path.exists():
        os.remove(file_path)
    raise
```

### 5. Import Errors
**Problem**: Missing Invoice model import causing startup failure
**Solution**: Import models in main.py:
```python
# Import models to register with SQLAlchemy
from app.models import user, invoice
```

## Testing Guide

### Manual Testing with curl

1. **Upload a file**:
```bash
# First get auth token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -F "username=test@example.com" \
  -F "password=password" \
  | jq -r '.access_token')

# Upload file
curl -X POST http://localhost:8000/api/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@invoice.pdf"
```

2. **List invoices**:
```bash
curl -X GET http://localhost:8000/api/invoices/ \
  -H "Authorization: Bearer $TOKEN"
```

3. **Test invalid file**:
```bash
curl -X POST http://localhost:8000/api/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt"
```

### Automated Testing
Use the provided `test_file_upload.py` script which tests:
- File upload with valid image
- Invoice retrieval
- Invoice listing
- Invoice deletion
- Invalid file type rejection
- Unauthorized access prevention

## Security Best Practices

### 1. File Type Validation
- Check both extension and MIME type
- Never trust client-provided data
- Whitelist allowed types explicitly

### 2. File Size Limits
- Implement reasonable limits (10MB default)
- Check size during streaming, not after
- Provide clear error messages

### 3. Path Traversal Prevention
- Use UUID filenames
- Never use user-provided filenames directly
- Validate all path components

### 4. User Isolation
- Separate directories per user
- Verify ownership before operations
- Use database relationships for access control

### 5. Cleanup Strategy
- Delete files when records deleted
- Handle orphaned files periodically
- Log all file operations

## Storage Considerations

### Directory Structure
```
uploads/
├── 1/                    # User ID 1
│   ├── uuid1.pdf
│   └── uuid2.jpg
├── 2/                    # User ID 2
│   └── uuid3.png
```

### File Naming
- Original: `Invoice_2024.pdf`
- Stored as: `a3f4d5e6-b7c8-9d0e-1f2g-3h4i5j6k7l8m.pdf`
- Database keeps both names

### Cleanup Policy
- Manual deletion via API
- Consider automated cleanup for old files
- Implement storage quotas per user

## Extension Activities

### 1. Image Preview Generation
Generate thumbnails for uploaded images:
```python
from PIL import Image

def create_thumbnail(image_path, size=(200, 200)):
    img = Image.open(image_path)
    img.thumbnail(size)
    # Save thumbnail
```

### 2. File Type Detection
Use python-magic for better MIME detection:
```python
import magic

mime = magic.from_file(file_path, mime=True)
```

### 3. Progress Tracking
Implement upload progress with streaming:
- Track bytes uploaded
- Send progress events
- Update UI progressively

### 4. Batch Upload
Support multiple file uploads:
```python
@router.post("/batch-upload")
async def upload_multiple(
    files: List[UploadFile] = File(...)
):
    # Process multiple files
```

### 5. Storage Backends
Abstract storage for flexibility:
- Local filesystem
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

## Debugging Tips

### 1. File Not Found
- Check upload directory exists
- Verify path construction
- Check file permissions

### 2. 413 Request Entity Too Large
- Nginx/reverse proxy limits
- FastAPI body size limits
- Client timeout settings

### 3. Slow Uploads
- Use chunked reading
- Optimize chunk size
- Consider async operations

### 4. Database Sync Issues
- Ensure transaction commits
- Handle rollbacks properly
- Check cascade settings

## Assessment Criteria

### Functional Requirements (70%)
- [ ] Files upload successfully
- [ ] Validation works correctly
- [ ] Files stored securely
- [ ] Metadata tracked in database
- [ ] Listing and retrieval work
- [ ] Deletion removes file and record

### Code Quality (20%)
- [ ] Proper error handling
- [ ] Async operations used correctly
- [ ] Clean separation of concerns
- [ ] No resource leaks

### Security (10%)
- [ ] File types validated
- [ ] Size limits enforced
- [ ] User isolation maintained
- [ ] Path traversal prevented

## Next Steps
After completing file uploads, students will:
1. STEP-007: Integrate AI for invoice data extraction
2. STEP-008: Build frontend file upload UI
3. STEP-009: Display extracted data

## Resources
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [aiofiles Documentation](https://github.com/Tinche/aiofiles)
- [Python UUID Module](https://docs.python.org/3/library/uuid.html)
- [Pillow Documentation](https://pillow.readthedocs.io/)

## Troubleshooting Checklist
- [ ] aiofiles installed?
- [ ] Upload directory created?
- [ ] File permissions correct?
- [ ] Database migrations run?
- [ ] Invoice model imported in main.py?
- [ ] Router included in main.py?
- [ ] Authentication working?
- [ ] Using multipart form data?

## Sample Solution Structure
```
backend/
├── app/
│   ├── api/
│   │   └── invoices.py      # ✨ NEW: Upload endpoints
│   ├── models/
│   │   ├── invoice.py       # ✨ NEW: Invoice model
│   │   └── user.py          # 📝 UPDATED: Relationship
│   ├── schemas/
│   │   └── invoice.py       # ✨ NEW: Invoice schemas
│   ├── services/
│   │   ├── file_service.py  # ✨ NEW: File operations
│   │   └── invoice_service.py # ✨ NEW: Invoice CRUD
│   └── main.py              # 📝 UPDATED: Import models
├── uploads/                  # ✨ NEW: File storage
│   └── {user_id}/
└── test_file_upload.py      # ✨ NEW: Test script
```

## Common Errors and Solutions

### Error: "No file provided"
**Cause**: Empty file field
**Solution**: Check file selection in frontend

### Error: "File type not allowed"
**Cause**: Invalid extension or MIME type
**Solution**: Use allowed formats (.pdf, .jpg, .jpeg, .png)

### Error: "File size exceeds maximum"
**Cause**: File larger than 10MB
**Solution**: Compress or resize before upload

### Error: "Could not save file"
**Cause**: Disk full or permissions
**Solution**: Check storage and permissions

This completes the file upload implementation!