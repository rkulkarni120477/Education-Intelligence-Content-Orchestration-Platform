"""File management service for Custom Content Development module."""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, BinaryIO
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'xlsx', 'csv', 'txt', 'md', 'json',
    'html', 'css', 'js', 'ts', 'tsx', 'jsx',
    'png', 'jpg', 'jpeg', 'gif', 'webp',
    'mp4', 'mp3', 'wav', 'webm'
}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads" / "custom-content"


class CustomContentFileService:
    """Handle file operations for custom content module."""

    @staticmethod
    def validate_file(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """Validate file type and size.

        Args:
            filename: Original filename
            file_size: File size in bytes

        Returns:
            (is_valid, error_message)
        """
        if file_size > MAX_FILE_SIZE:
            return False, f"File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit"

        ext = Path(filename).suffix.lstrip('.').lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"File type .{ext} not allowed"

        return True, None

    @staticmethod
    def save_file(file_content: bytes, original_filename: str) -> tuple[str, str, int]:
        """Save uploaded file to disk.

        Args:
            file_content: File binary content
            original_filename: Original filename

        Returns:
            (file_id, file_path, file_size)
        """
        try:
            # Create upload directory
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

            # Generate unique ID
            file_id = str(uuid.uuid4())

            # Preserve extension
            suffix = Path(original_filename).suffix.lower()
            file_path = UPLOAD_DIR / f"{file_id}{suffix}"

            # Write file
            with file_path.open('wb') as f:
                f.write(file_content)

            file_size = len(file_content)
            logger.info(f"Saved file {file_id}: {original_filename} ({file_size} bytes)")

            return file_id, str(file_path), file_size

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from disk.

        Args:
            file_path: Full path to file

        Returns:
            True if deleted, False if file not found
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            raise

    @staticmethod
    def read_file(file_path: str) -> bytes:
        """Read file content from disk.

        Args:
            file_path: Full path to file

        Returns:
            File binary content
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with path.open('rb') as f:
                return f.read()

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise

    @staticmethod
    def read_file_text(file_path: str, encoding: str = 'utf-8') -> str:
        """Read text file content.

        Args:
            file_path: Full path to file
            encoding: Text encoding (default utf-8)

        Returns:
            File text content
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with path.open('r', encoding=encoding) as f:
                return f.read()

        except UnicodeDecodeError:
            # Try latin-1 as fallback
            with path.open('r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {str(e)}")
            raise

    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Get MIME type for file.

        Args:
            filename: Filename

        Returns:
            MIME type string
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'

    @staticmethod
    def get_file_size_mb(size_bytes: int) -> float:
        """Convert bytes to megabytes.

        Args:
            size_bytes: Size in bytes

        Returns:
            Size in megabytes
        """
        return round(size_bytes / (1024 * 1024), 2)

    @staticmethod
    def cleanup_old_files(days: int = 30) -> int:
        """Delete files older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of files deleted
        """
        try:
            from datetime import timedelta, timezone

            threshold = datetime.now(timezone.utc) - timedelta(days=days)
            deleted_count = 0

            if not UPLOAD_DIR.exists():
                return 0

            for file_path in UPLOAD_DIR.glob('*'):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(
                        file_path.stat().st_mtime,
                        tz=timezone.utc
                    )
                    if mtime < threshold:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Cleaned up old file: {file_path.name}")

            logger.info(f"Cleanup complete: {deleted_count} files deleted")
            return deleted_count

        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
            return 0
