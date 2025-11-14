"""Unit tests for validation utilities.

Tests cover:
- File size validation (max 100MB)
- MIME type validation (application/pdf)
- Filename validation (sanitization, path traversal prevention)
- PDF format validation (magic bytes)
- Combined validation function
"""

import io
from typing import BinaryIO

import pytest

from src.utils.validators import (
    MAX_FILE_SIZE_BYTES,
    PDF_MAGIC_BYTES,
    ValidationError,
    validate_file_size,
    validate_filename,
    validate_mime_type,
    validate_pdf_format,
    validate_pdf_upload,
)


class TestValidateFileSize:
    """Test cases for file size validation."""

    def test_valid_file_size(self):
        """Test that valid file sizes pass validation."""
        # Small file
        validate_file_size(1024)  # 1 KB

        # Medium file
        validate_file_size(10 * 1024 * 1024)  # 10 MB

        # Maximum allowed size
        validate_file_size(MAX_FILE_SIZE_BYTES)  # 100 MB

    def test_zero_file_size(self):
        """Test that zero file size raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(0)

        assert exc_info.value.error_code == "INVALID_FILE_SIZE"
        assert "greater than 0" in exc_info.value.message

    def test_negative_file_size(self):
        """Test that negative file size raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(-1)

        assert exc_info.value.error_code == "INVALID_FILE_SIZE"

    def test_file_too_large(self):
        """Test that files exceeding max size raise error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(MAX_FILE_SIZE_BYTES + 1)

        assert exc_info.value.error_code == "FILE_TOO_LARGE"
        assert "100MB" in exc_info.value.message

    def test_file_much_too_large(self):
        """Test that extremely large files raise error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(500 * 1024 * 1024)  # 500 MB

        assert exc_info.value.error_code == "FILE_TOO_LARGE"


class TestValidateMimeType:
    """Test cases for MIME type validation."""

    def test_valid_mime_type(self):
        """Test that application/pdf MIME type passes validation."""
        validate_mime_type("application/pdf")

    def test_empty_mime_type(self):
        """Test that empty MIME type raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_mime_type("")

        assert exc_info.value.error_code == "MISSING_MIME_TYPE"

    def test_invalid_mime_types(self):
        """Test that non-PDF MIME types raise error."""
        invalid_types = [
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "image/jpeg",
            "image/png",
            "application/octet-stream",
        ]

        for mime_type in invalid_types:
            with pytest.raises(ValidationError) as exc_info:
                validate_mime_type(mime_type)

            assert exc_info.value.error_code == "INVALID_MIME_TYPE"
            assert "PDF" in exc_info.value.message
            assert mime_type in exc_info.value.message


class TestValidateFilename:
    """Test cases for filename validation and sanitization."""

    def test_valid_filenames(self):
        """Test that valid filenames pass validation and return sanitized."""
        test_cases = [
            ("document.pdf", "document.pdf"),
            ("my-file_name.pdf", "my-file_name.pdf"),
            ("Report 2024.pdf", "Report 2024.pdf"),
            ("file with spaces.pdf", "file with spaces.pdf"),
            ("résumé.pdf", "résumé.pdf"),  # Unicode characters
        ]

        for original, expected in test_cases:
            result = validate_filename(original)
            assert result == expected

    def test_empty_filename(self):
        """Test that empty filename raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_filename("")

        assert exc_info.value.error_code == "INVALID_FILENAME"
        assert "empty" in exc_info.value.message.lower()

    def test_filename_too_long(self):
        """Test that filenames exceeding max length raise error."""
        long_filename = "a" * 256 + ".pdf"
        with pytest.raises(ValidationError) as exc_info:
            validate_filename(long_filename)

        assert exc_info.value.error_code == "INVALID_FILENAME"
        assert "255" in exc_info.value.message

    def test_path_traversal_attempts(self):
        """Test that path traversal sequences are rejected."""
        malicious_filenames = [
            "../etc/passwd.pdf",
            "..\\windows\\system32\\file.pdf",
            "../../file.pdf",
            "/etc/passwd.pdf",
            "\\windows\\file.pdf",
            "subdir/../../../file.pdf",
        ]

        for filename in malicious_filenames:
            with pytest.raises(ValidationError) as exc_info:
                validate_filename(filename)

            assert exc_info.value.error_code == "INVALID_FILENAME"
            assert (
                "traversal" in exc_info.value.message.lower()
                or "invalid" in exc_info.value.message.lower()
            )

    def test_null_byte_in_filename(self):
        """Test that filenames with null bytes are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_filename("file\x00name.pdf")

        assert exc_info.value.error_code == "INVALID_FILENAME"
        assert "null" in exc_info.value.message.lower()

    def test_filename_without_pdf_extension(self):
        """Test that non-PDF extensions are rejected."""
        invalid_filenames = [
            "document.txt",
            "image.jpg",
            "file.docx",
            "noextension",
        ]

        for filename in invalid_filenames:
            with pytest.raises(ValidationError) as exc_info:
                validate_filename(filename)

            assert exc_info.value.error_code == "INVALID_FILENAME"
            assert ".pdf" in exc_info.value.message.lower()

    def test_filename_sanitization(self):
        """Test that filenames are properly sanitized."""
        test_cases = [
            # Multiple spaces reduced to single space
            ("file   with   spaces.pdf", "file with spaces.pdf"),
            # Leading/trailing periods removed
            (".file.pdf", "file.pdf"),
            # Leading/trailing whitespace removed
            ("  file.pdf  ", "file.pdf"),
            # Tabs and newlines replaced with space
            ("file\twith\ttabs.pdf", "file with tabs.pdf"),
        ]

        for original, expected in test_cases:
            result = validate_filename(original)
            assert result == expected

    def test_filename_with_only_periods_and_spaces(self):
        """Test that filenames with periods and spaces are properly sanitized."""
        # After stripping whitespace and leading/trailing periods
        result = validate_filename("  . .pdf  ")
        # Leading periods are stripped, extra spaces reduced
        assert (
            result == " .pdf"
        )  # Space before period is kept after stripping leading periods

    def test_case_insensitive_pdf_extension(self):
        """Test that PDF extension check is case-insensitive."""
        valid_extensions = [
            "file.pdf",
            "file.PDF",
            "file.Pdf",
            "file.pDf",
        ]

        for filename in valid_extensions:
            result = validate_filename(filename)
            assert result == filename


class TestValidatePdfFormat:
    """Test cases for PDF format validation (magic bytes)."""

    def test_valid_pdf_bytes(self):
        """Test that valid PDF content passes validation."""
        pdf_content = PDF_MAGIC_BYTES + b"1.4\n%some pdf content"
        validate_pdf_format(pdf_content)

    def test_valid_pdf_file_like_object(self):
        """Test that valid PDF file-like object passes validation."""
        pdf_content = PDF_MAGIC_BYTES + b"1.4\n%some pdf content"
        pdf_file = io.BytesIO(pdf_content)
        validate_pdf_format(pdf_file)

        # Verify file pointer is reset
        assert pdf_file.tell() == 0

    def test_empty_content(self):
        """Test that empty content raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pdf_format(b"")

        assert exc_info.value.error_code == "INVALID_PDF"
        assert "empty" in exc_info.value.message.lower()

    def test_invalid_magic_bytes(self):
        """Test that content without PDF magic bytes raises error."""
        invalid_contents = [
            b"Not a PDF file",
            b"\x89PNG\r\n\x1a\n",  # PNG header
            b"PK\x03\x04",  # ZIP header
            b"%!PS-Adobe-3.0",  # PostScript header
        ]

        for content in invalid_contents:
            with pytest.raises(ValidationError) as exc_info:
                validate_pdf_format(content)

            assert exc_info.value.error_code == "INVALID_PDF"
            assert "signature" in exc_info.value.message.lower()

    def test_partial_pdf_header(self):
        """Test that incomplete PDF header raises error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pdf_format(b"%PD")

        assert exc_info.value.error_code == "INVALID_PDF"

    def test_pdf_header_not_at_start(self):
        """Test that PDF header must be at the start of file."""
        content = b"Some garbage" + PDF_MAGIC_BYTES + b"1.4\n"
        with pytest.raises(ValidationError) as exc_info:
            validate_pdf_format(content)

        assert exc_info.value.error_code == "INVALID_PDF"


class TestValidatePdfUpload:
    """Test cases for combined PDF upload validation."""

    def test_valid_pdf_upload(self):
        """Test that valid PDF upload passes all validations."""
        filename = "document.pdf"
        file_size = 10 * 1024 * 1024  # 10 MB
        mime_type = "application/pdf"
        file_content = PDF_MAGIC_BYTES + b"1.4\n%PDF content"

        sanitized = validate_pdf_upload(filename, file_size, mime_type, file_content)

        assert sanitized == filename

    def test_valid_pdf_upload_without_content(self):
        """Test that validation works without file content."""
        filename = "document.pdf"
        file_size = 10 * 1024 * 1024  # 10 MB
        mime_type = "application/pdf"

        sanitized = validate_pdf_upload(filename, file_size, mime_type)

        assert sanitized == filename

    def test_upload_fails_on_file_size(self):
        """Test that upload validation fails on file size."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pdf_upload(
                "document.pdf",
                MAX_FILE_SIZE_BYTES + 1,
                "application/pdf",
            )

        assert exc_info.value.error_code == "FILE_TOO_LARGE"

    def test_upload_fails_on_mime_type(self):
        """Test that upload validation fails on MIME type."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pdf_upload(
                "document.pdf",
                1024,
                "application/msword",
            )

        assert exc_info.value.error_code == "INVALID_MIME_TYPE"

    def test_upload_fails_on_filename(self):
        """Test that upload validation fails on invalid filename."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pdf_upload(
                "../etc/passwd.pdf",
                1024,
                "application/pdf",
            )

        assert exc_info.value.error_code == "INVALID_FILENAME"

    def test_upload_fails_on_pdf_format(self):
        """Test that upload validation fails on PDF format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pdf_upload(
                "document.pdf",
                1024,
                "application/pdf",
                b"Not a PDF",
            )

        assert exc_info.value.error_code == "INVALID_PDF"

    def test_upload_sanitizes_filename(self):
        """Test that upload validation sanitizes filename."""
        sanitized = validate_pdf_upload(
            "  file   with   spaces.pdf  ",
            1024,
            "application/pdf",
        )

        assert sanitized == "file with spaces.pdf"


class TestValidationErrorClass:
    """Test cases for ValidationError exception class."""

    def test_validation_error_attributes(self):
        """Test that ValidationError has correct attributes."""
        error = ValidationError("TEST_ERROR", "Test message")

        assert error.error_code == "TEST_ERROR"
        assert error.message == "Test message"
        assert str(error) == "TEST_ERROR: Test message"

    def test_validation_error_inheritance(self):
        """Test that ValidationError is an Exception."""
        error = ValidationError("TEST_ERROR", "Test message")
        assert isinstance(error, Exception)
