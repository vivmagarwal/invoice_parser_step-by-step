"""
File Management Service

Handles secure file upload, storage, and access with user isolation.
"""
import os
import logging
import shutil
from datetime import datetime
from typing import Optional, Tuple, List
from pathlib import Path
import uuid

from fastapi import UploadFile
from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class FileService:
    """Service for managing user file uploads with isolation."""
    
    def __init__(self):
        """Initialize file service with upload directory."""
        self.upload_base_dir = Path("uploads")
        self.upload_base_dir.mkdir(exist_ok=True)
        
    def _get_user_upload_dir(self, user_id: str) -> Path:
        """Get user-specific upload directory."""
        user_dir = self.upload_base_dir / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir
    
    def _generate_secure_filename(self, original_filename: str) -> str:
        """Generate secure filename with timestamp and UUID."""
        # Get file extension
        file_ext = Path(original_filename).suffix.lower()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate short UUID for uniqueness
        unique_id = str(uuid.uuid4())[:8]
        
        # Clean original filename (remove extension and special chars)
        clean_name = Path(original_filename).stem
        clean_name = "".join(c for c in clean_name if c.isalnum() or c in ('-', '_'))[:20]
        
        return f"{timestamp}_{unique_id}_{clean_name}{file_ext}"
    
    async def save_uploaded_file(
        self, 
        file: UploadFile, 
        user_id: str
    ) -> Tuple[str, dict]:
        """
        Save uploaded file to user-specific directory.
        
        Args:
            file: Uploaded file object
            user_id: User UUID string
            
        Returns:
            Tuple of (file_id, file_info_dict)
        """
        try:
            # Validate file
            if not file.filename:
                raise ValueError("No filename provided")
            
            # Get user directory
            user_dir = self._get_user_upload_dir(user_id)
            
            # Generate secure filename
            secure_filename = self._generate_secure_filename(file.filename)
            file_path = user_dir / secure_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Generate file ID (relative path from uploads dir)
            file_id = f"{user_id}/{secure_filename}"
            
            # Get file info
            file_info = {
                "file_id": file_id,
                "original_name": file.filename,
                "secure_filename": secure_filename,
                "file_path": str(file_path),
                "relative_path": file_id,
                "size": len(content),
                "content_type": file.content_type,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"File saved: {file_id} ({len(content)} bytes)")
            return file_id, file_info
            
        except Exception as e:
            logger.error(f"Error saving file for user {user_id}: {e}")
            raise
    
    def get_file_path(self, file_id: str, user_id: str) -> Optional[Path]:
        """
        Get file path if user has access to it.
        
        Args:
            file_id: File identifier (user_id/filename format)
            user_id: Requesting user ID
            
        Returns:
            Path object if file exists and user has access, None otherwise
        """
        try:
            # Parse file_id to extract user and filename
            if "/" not in file_id:
                return None
            
            file_user_id, filename = file_id.split("/", 1)
            
            # Check if user has access to this file
            if file_user_id != user_id:
                logger.warning(f"User {user_id} attempted to access file {file_id} (unauthorized)")
                return None
            
            # Check if file exists
            file_path = self.upload_base_dir / file_id
            if not file_path.exists():
                logger.warning(f"File not found: {file_id}")
                return None
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error getting file path {file_id} for user {user_id}: {e}")
            return None
    
    def delete_file(self, file_id: str, user_id: str) -> bool:
        """
        Delete file if user has access to it.
        
        Args:
            file_id: File identifier
            user_id: Requesting user ID
            
        Returns:
            True if file was deleted, False otherwise
        """
        try:
            file_path = self.get_file_path(file_id, user_id)
            if not file_path:
                return False
            
            # Delete file
            file_path.unlink()
            logger.info(f"File deleted: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id} for user {user_id}: {e}")
            return False
    
    def get_user_files(self, user_id: str) -> List[dict]:
        """
        Get list of files for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of file info dictionaries
        """
        try:
            user_dir = self._get_user_upload_dir(user_id)
            files = []
            
            for file_path in user_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    stat = file_path.stat()
                    file_info = {
                        "file_id": f"{user_id}/{file_path.name}",
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                    files.append(file_info)
            
            # Sort by creation time (newest first)
            files.sort(key=lambda x: x["created_at"], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"Error getting files for user {user_id}: {e}")
            return []
    
    def get_user_storage_stats(self, user_id: str) -> dict:
        """
        Get storage statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with storage statistics
        """
        try:
            user_dir = self._get_user_upload_dir(user_id)
            
            total_size = 0
            file_count = 0
            
            for file_path in user_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "file_count": file_count,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "directory": str(user_dir)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats for user {user_id}: {e}")
            return {
                "file_count": 0,
                "total_size": 0,
                "total_size_mb": 0.0,
                "directory": ""
            }
    
    def cleanup_user_files(self, user_id: str, days_old: int = 30) -> int:
        """
        Clean up old files for a user.
        
        Args:
            user_id: User ID
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        try:
            user_dir = self._get_user_upload_dir(user_id)
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            for file_path in user_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Cleaned up old file: {file_path}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up files for user {user_id}: {e}")
            return 0
    
    def generate_thumbnail(self, file_path: Path, size: int = 150) -> Optional[Path]:
        """
        Generate a thumbnail for an image file.
        
        Args:
            file_path: Path to the original image file
            size: Thumbnail size in pixels (square)
            
        Returns:
            Path to generated thumbnail or None if failed
        """
        try:
            from PIL import Image
            import os
            
            # Create thumbnails directory
            thumbnails_dir = self.upload_base_dir / "thumbnails"
            thumbnails_dir.mkdir(exist_ok=True)
            
            # Generate thumbnail filename
            file_stem = file_path.stem
            thumbnail_name = f"{file_stem}_{size}.jpg"
            thumbnail_path = thumbnails_dir / thumbnail_name
            
            # Check if thumbnail already exists
            if thumbnail_path.exists():
                return thumbnail_path
            
            # Open and resize image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create thumbnail maintaining aspect ratio
                img.thumbnail((size, size), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                img.save(thumbnail_path, "JPEG", quality=85)
                
            logger.info(f"Generated thumbnail: {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Error generating thumbnail for {file_path}: {e}")
            return None