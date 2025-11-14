"""Validation utilities for file uploads and input validation.

This module provides reusable validation functions for:
- File size validation (max 100MB)
- MIME type validation (application/pdf only)
- Filename validation (sanitize special characters, prevent path traversal)
- PDF format validation (check magic bytes)
"""

import re
from typing import BinaryIO, Optional, Union


class ValidationError(Exception):
    """Custom exception for validation errors with error codes.

    Attributes:
        error_code: Machine-readable error code (e.g., "INVALID_FILE_SIZE")
        message: Human-readable error message
    """

    def __init__(self, error_code: str, message: str):
        """Initialize ValidationError with error code and message.

        Args:
            error_code: Machine-readable error code
            message: Human-readable error message
        """
        self.error_code = error_code
        self.message = message
        super().__init__(f"{error_code}: {message}")


# Constants for validation
MAX_FILE_SIZE_BYTES = 104857600  # 100 MB
ALLOWED_MIME_TYPE = "application/pdf"
MAX_FILENAME_LENGTH = 255
PDF_MAGIC_BYTES = b"%PDF-"


def validate_file_size(file_size: int) -> None:
    """Validate that file size is within allowed limits.

    Args:
        file_size: Size of the file in bytes

    Raises:
        ValidationError: If file size exceeds MAX_FILE_SIZE_BYTES (100MB)
    """
    if file_size <= 0:
        raise ValidationError(
            "INVALID_FILE_SIZE",
            "File size must be greater than 0 bytes",
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        max_size_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise ValidationError(
            "FILE_TOO_LARGE",
            f"File size exceeds maximum allowed size of {max_size_mb:.0f}MB",
        )


def validate_mime_type(mime_type: str) -> None:
    """Validate that MIME type is allowed (application/pdf only).

    Args:
        mime_type: MIME type of the uploaded file

    Raises:
        ValidationError: If MIME type is not application/pdf
    """
    if not mime_type:
        raise ValidationError(
            "MISSING_MIME_TYPE",
            "MIME type is required",
        )

    if mime_type != ALLOWED_MIME_TYPE:
        raise ValidationError(
            "INVALID_MIME_TYPE",
            f"Only PDF files are allowed. Got: {mime_type}",
        )


def validate_filename(filename: str) -> str:
    r"""Validate and sanitize filename.

    Validates that:
    - Filename is not empty
    - Filename length doesn't exceed MAX_FILENAME_LENGTH (255 characters)
    - Filename doesn't contain path traversal sequences (../, ..\\, etc.)
    - Filename contains only safe characters

    Args:
        filename: Original filename from upload

    Returns:
        Sanitized filename safe for storage

    Raises:
        ValidationError: If filename is invalid or contains unsafe patterns
    """
    if not filename:
        raise ValidationError(
            "INVALID_FILENAME",
            "Filename cannot be empty",
        )

    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValidationError(
            "INVALID_FILENAME",
            f"Filename exceeds maximum length of {MAX_FILENAME_LENGTH} characters",
        )

    # Check for path traversal attempts (../ or ..\\ patterns)
    if (
        "../" in filename
        or "..\\" in filename
        or filename.startswith("/")
        or filename.startswith("\\")
    ):
        raise ValidationError(
            "INVALID_FILENAME",
            "Filename contains invalid path traversal sequences",
        )

    # Check for null bytes (security risk)
    if "\x00" in filename:
        raise ValidationError(
            "INVALID_FILENAME",
            "Filename contains null bytes",
        )

    # Sanitize filename: allow alphanumeric, spaces, hyphens, underscores,
    # periods, and common unicode characters
    # Remove or replace potentially dangerous characters
    sanitized = filename.strip()

    # Replace multiple consecutive spaces with a single space
    sanitized = re.sub(r"\s+", " ", sanitized)

    # Remove leading/trailing periods (can cause issues on some filesystems)
    sanitized = sanitized.strip(".")

    if not sanitized:
        raise ValidationError(
            "INVALID_FILENAME",
            "Filename is empty after sanitization",
        )

    # Ensure filename has .pdf extension (case-insensitive)
    if not sanitized.lower().endswith(".pdf"):
        raise ValidationError(
            "INVALID_FILENAME",
            "Filename must have .pdf extension",
        )

    return sanitized


def validate_pdf_format(
    file_content: Union[bytes, BinaryIO], max_bytes_to_check: int = 1024
) -> None:
    """Validate PDF format by checking magic bytes.

    PDF files must start with %PDF- signature (magic bytes).
    This function checks the first few bytes of the file.

    Args:
        file_content: File content as bytes or file-like object
        max_bytes_to_check: Maximum number of bytes to read from start

    Raises:
        ValidationError: If file doesn't have PDF magic bytes signature
    """
    # Handle both bytes and file-like objects
    if isinstance(file_content, bytes):
        header = file_content[:max_bytes_to_check]
    else:
        # File-like object - read and reset position
        current_pos = file_content.tell()
        header = file_content.read(max_bytes_to_check)
        file_content.seek(current_pos)

    if not header:
        raise ValidationError(
            "INVALID_PDF",
            "File is empty or cannot be read",
        )

    # Check for PDF magic bytes at the start of the file
    if not header.startswith(PDF_MAGIC_BYTES):
        raise ValidationError(
            "INVALID_PDF",
            "File is not a valid PDF (missing PDF signature)",
        )


def validate_pdf_upload(
    filename: str,
    file_size: int,
    mime_type: str,
    file_content: Optional[Union[bytes, BinaryIO]] = None,
) -> str:
    """Validate all aspects of a PDF upload.

    Combines all validation functions into a single comprehensive check.
    This is the recommended function to use for validating PDF uploads.

    Args:
        filename: Original filename from upload
        file_size: Size of file in bytes
        mime_type: MIME type of the uploaded file
        file_content: Optional file content for magic bytes validation

    Returns:
        Sanitized filename safe for storage

    Raises:
        ValidationError: If any validation check fails
    """
    # Validate file size
    validate_file_size(file_size)

    # Validate MIME type
    validate_mime_type(mime_type)

    # Validate and sanitize filename
    sanitized_filename = validate_filename(filename)

    # Validate PDF format if content is provided
    if file_content is not None:
        validate_pdf_format(file_content)

    return sanitized_filename
