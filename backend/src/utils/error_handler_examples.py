"""Example usage of the error handling framework.

This module demonstrates how to use ErrorCode, AppError, and retry_with_backoff
in various scenarios throughout the application.
"""

import asyncio
from src.utils.error_handler import AppError, ErrorCode, retry_with_backoff


# Example 1: Basic AppError usage
def validate_pdf_file(file_size: int, max_size: int = 100_000_000):
    """Validate PDF file size."""
    if file_size > max_size:
        raise AppError(
            error_code=ErrorCode.FILE_TOO_LARGE,
            message=f"File size {file_size} bytes exceeds maximum {max_size} bytes",
            details={"size": file_size, "limit": max_size},
            status_code=400,
            is_retryable=False,
        )


# Example 2: Retry decorator for API calls
@retry_with_backoff(
    max_retries=3,
    initial_delay=1.0,
    retryable_error_codes={ErrorCode.RATE_LIMITED, ErrorCode.TIMEOUT},
)
async def call_gemini_api(prompt: str) -> dict:
    """Make API call to Gemini with automatic retry on rate limits."""
    # Simulated API call
    import random

    if random.random() < 0.3:  # 30% chance of rate limit
        raise AppError(
            error_code=ErrorCode.RATE_LIMITED,
            message="Rate limit exceeded",
            details={"retry_after": 2},
            status_code=429,
            is_retryable=True,
        )

    return {"response": "Generated content", "tokens": 100}


# Example 3: Database operations with retry
@retry_with_backoff(
    max_retries=5,
    initial_delay=0.5,
    retryable_error_codes={ErrorCode.DB_CONNECTION_ERROR},
)
def save_document_to_db(document_data: dict):
    """Save document to database with retry on connection errors."""
    # Simulated database save
    print(f"Saving document: {document_data.get('filename')}")
    return {"id": 1, "status": "saved"}


# Example 4: Custom retry callback for logging
def on_retry_callback(exception: Exception, attempt: int, delay: float):
    """Log retry attempts for monitoring."""
    print(f"Retry attempt {attempt} after {delay:.2f}s: {exception}")


@retry_with_backoff(
    max_retries=3, initial_delay=1.0, on_retry=on_retry_callback
)
async def process_with_monitoring():
    """Process operation with retry monitoring."""
    # Your processing logic here
    pass


# Example 5: Error handling in service layer
class DocumentService:
    """Example service using error handling framework."""

    async def upload_document(self, file_data: bytes, filename: str) -> dict:
        """Upload and process a document."""
        # Validate file size
        file_size = len(file_data)
        if file_size > 100_000_000:
            raise AppError(
                error_code=ErrorCode.FILE_TOO_LARGE,
                message="File exceeds maximum size",
                details={"filename": filename, "size": file_size},
                status_code=400,
            )

        # Process document with retry
        try:
            result = await self._process_document(file_data)
            return result
        except Exception as e:
            raise AppError(
                error_code=ErrorCode.PARSING_ERROR,
                message=f"Failed to parse document: {str(e)}",
                details={"filename": filename},
                status_code=500,
            )

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def _process_document(self, file_data: bytes) -> dict:
        """Process document content with automatic retry."""
        # Your processing logic here
        return {"status": "processed", "page_count": 10}


# Example 6: HTTP status code mapping
def handle_app_error(error: AppError) -> dict:
    """Convert AppError to HTTP response."""
    return {
        "status_code": error.status_code,
        "body": error.to_dict(),
    }


if __name__ == "__main__":
    # Demo basic error handling
    try:
        validate_pdf_file(150_000_000)
    except AppError as e:
        print(f"Error: {e}")
        print(f"Error dict: {e.to_dict()}")

    # Demo async retry
    asyncio.run(call_gemini_api("Test prompt"))
