"""
File Management Routes

Handles secure file upload, download, and management with user isolation.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse

from app.services.file_service import FileService
from app.models.database import UserModel
from app.api.routes.auth import get_current_user

router = APIRouter(tags=["files"])

# Configure logging
logger = logging.getLogger(__name__)


def get_file_service() -> FileService:
    """Dependency to get file service instance."""
    return FileService()


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    Upload file to user-specific directory.
    
    Args:
        file: Uploaded file
        current_user: Authenticated user
        file_service: File service instance
        
    Returns:
        File information including file_id for future reference
    """
    try:
        # Validate file type (same as existing validation)
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Supported: {', '.join(allowed_types)}"
            )
        
        # Validate file size (10MB max)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Reset file position for saving
        await file.seek(0)
        
        # Save file
        file_id, file_info = await file_service.save_uploaded_file(file, str(current_user.id))
        
        logger.info(f"File uploaded by {current_user.email}: {file_id}")
        
        return {
            "success": True,
            "file_id": file_id,
            "original_name": file_info["original_name"],
            "size": file_info["size"],
            "content_type": file_info["content_type"],
            "created_at": file_info["created_at"],
            "message": "File uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@router.get("/files/{file_id}")
async def download_file(
    file_id: str,
    current_user: UserModel = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    Download file (only if user owns it).
    
    Args:
        file_id: File identifier
        current_user: Authenticated user
        file_service: File service instance
        
    Returns:
        File response for download
    """
    try:
        # Get file path (includes access control check)
        file_path = file_service.get_file_path(file_id, str(current_user.id))
        
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        
        # Extract original filename for download
        filename = file_path.name
        
        logger.info(f"File downloaded by {current_user.email}: {file_id}")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )


@router.get("/files/{file_id}/thumbnail")
async def get_file_thumbnail(
    file_id: str,
    size: int = Query(150, ge=50, le=500, description="Thumbnail size in pixels"),
    current_user: UserModel = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    Get thumbnail of an image file (only if user owns it).
    
    Args:
        file_id: File identifier
        size: Thumbnail size in pixels (default: 150)
        current_user: Authenticated user
        file_service: File service instance
        
    Returns:
        Thumbnail image response
    """
    try:
        # Get file path (includes access control check)
        file_path = file_service.get_file_path(file_id, str(current_user.id))
        
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        
        # Generate thumbnail
        thumbnail_path = file_service.generate_thumbnail(file_path, size)
        
        if not thumbnail_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate thumbnail"
            )
        
        return FileResponse(
            path=thumbnail_path,
            media_type="image/jpeg",
            filename=f"thumbnail_{file_id}.jpg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thumbnail for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get thumbnail"
        )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: UserModel = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    Delete file (only if user owns it).
    
    Args:
        file_id: File identifier
        current_user: Authenticated user
        file_service: File service instance
        
    Returns:
        Success message
    """
    try:
        # Delete file (includes access control check)
        success = file_service.delete_file(file_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        
        logger.info(f"File deleted by {current_user.email}: {file_id}")
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@router.get("/files")
async def list_user_files(
    current_user: UserModel = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """
    List all files for the current user.
    
    Args:
        current_user: Authenticated user
        file_service: File service instance
        
    Returns:
        List of user's files with metadata
    """
    try:
        files = file_service.get_user_files(str(current_user.id))
        storage_stats = file_service.get_user_storage_stats(str(current_user.id))
        
        return {
            "files": files,
            "storage_stats": storage_stats,
            "total_files": len(files)
        }
        
    except Exception as e:
        logger.error(f"Error listing files for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )