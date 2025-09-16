import os
import uuid
import shutil
from typing import Optional
from pathlib import Path
from fastapi import UploadFile, HTTPException
import aiofiles


class FileService:
    """Service for handling file uploads and storage."""

    # Allowed file extensions for invoices
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}

    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

    # Upload directory
    UPLOAD_DIR = Path("uploads")

    @classmethod
    def get_upload_directory(cls, user_id: int) -> Path:
        """Get or create user-specific upload directory."""
        user_dir = cls.UPLOAD_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    @classmethod
    def validate_file(cls, file: UploadFile) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file.

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if file exists
        if not file.filename:
            return False, "No file provided"

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}"

        # Check MIME type
        allowed_mimes = {
            'application/pdf',
            'image/jpeg',
            'image/jpg',
            'image/png'
        }
        if file.content_type not in allowed_mimes:
            return False, f"Invalid file type. Content type: {file.content_type}"

        # File size check will be done during upload
        return True, None

    @classmethod
    async def save_file(cls, file: UploadFile, user_id: int) -> dict:
        """
        Save uploaded file to disk.

        Args:
            file: The uploaded file
            user_id: ID of the user uploading the file

        Returns:
            dict: File information including path, size, etc.
        """
        # Validate file
        is_valid, error_message = cls.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Get user upload directory
        upload_dir = cls.get_upload_directory(user_id)
        file_path = upload_dir / unique_filename

        # Save file
        file_size = 0
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                while content := await file.read(8192):  # Read in chunks
                    file_size += len(content)

                    # Check file size
                    if file_size > cls.MAX_FILE_SIZE:
                        # Delete partially uploaded file
                        await f.close()
                        os.remove(file_path)
                        raise HTTPException(
                            status_code=400,
                            detail=f"File size exceeds maximum allowed size of {cls.MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
                        )

                    await f.write(content)

        except Exception as e:
            # Clean up on error
            if file_path.exists():
                os.remove(file_path)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "mime_type": file.content_type
        }

    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """
        Delete a file from disk.

        Args:
            file_path: Path to the file to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                os.remove(path)
                return True
            return False
        except Exception:
            return False

    @classmethod
    def get_file_path(cls, filename: str, user_id: int) -> Optional[Path]:
        """
        Get full path for a file.

        Args:
            filename: Name of the file
            user_id: ID of the user who owns the file

        Returns:
            Path object if file exists, None otherwise
        """
        file_path = cls.get_upload_directory(user_id) / filename
        return file_path if file_path.exists() else None