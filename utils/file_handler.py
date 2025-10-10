"""
File handling utilities for uploads and downloads.
"""
from pathlib import Path
from typing import Optional
import shutil
from uuid import uuid4
from loguru import logger

from config import settings


class FileHandler:
    """Handle file uploads and downloads."""
    
    def __init__(self):
        """Initialize file handler."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    async def save_upload(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to upload directory.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_extension = Path(filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"File saved: {file_path}")
        return str(file_path)
    
    def validate_file_type(self, filename: str, file_type: str = "image") -> bool:
        """
        Validate file type based on extension.
        
        Args:
            filename: Filename to validate
            file_type: Type of file ("image" or "video")
            
        Returns:
            True if valid
        """
        extension = Path(filename).suffix.lower()
        
        if file_type == "image":
            return extension in settings.ALLOWED_IMAGE_EXTENSIONS
        elif file_type == "video":
            return extension in settings.ALLOWED_VIDEO_EXTENSIONS
        
        return False
    
    def get_file_path(self, filename: str, directory: str = "output") -> Optional[Path]:
        """
        Get full path to a file.
        
        Args:
            filename: Filename
            directory: Directory type ("output" or "upload")
            
        Returns:
            Path to file if exists, None otherwise
        """
        base_dir = self.output_dir if directory == "output" else self.upload_dir
        file_path = base_dir / filename
        
        return file_path if file_path.exists() else None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old uploaded and output files.
        
        Args:
            max_age_hours: Maximum file age in hours
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for directory in [self.upload_dir, self.output_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        logger.info(f"Deleted old file: {file_path}")


# Create singleton instance
file_handler = FileHandler()


