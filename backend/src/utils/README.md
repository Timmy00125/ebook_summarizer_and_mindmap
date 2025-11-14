# Error Handling Framework

Comprehensive error handling framework for the Ebook Summarizer backend with structured error codes, automatic retry logic, and graceful degradation strategies.

## Features

- **ErrorCode Enum**: Standardized error codes for consistent error handling
- **AppError Exception**: Custom exception class with structured error information
- **retry_with_backoff**: Decorator for automatic retry with exponential backoff
- **Graceful Degradation**: Utilities for fallback behavior on errors
- **Structured Logging**: Integration with Python logging framework
- **HTTP Status Mapping**: Automatic HTTP status code assignment

## Quick Start

### Basic Error Handling

```python
from src.utils.error_handler import AppError, ErrorCode

# Raise a structured error
raise AppError(
    error_code=ErrorCode.INVALID_PDF,
    message="Invalid PDF file format",
    details={"filename": "document.pdf"},
    status_code=400,
    is_retryable=False
)
```

### Automatic Retry

```python
from src.utils.error_handler import retry_with_backoff, ErrorCode

@retry_with_backoff(
    max_retries=3,
    initial_delay=1.0,
    retryable_error_codes={ErrorCode.RATE_LIMITED, ErrorCode.TIMEOUT}
)
async def call_external_api():
    # Your API call here
    pass
```

### Graceful Degradation

```python
from src.utils.error_handler import GracefulDegradation

# Sync function with fallback
result = GracefulDegradation.with_fallback(
    risky_operation,
    fallback_value="default_value",
    exceptions=(ValueError, TypeError)
)()

# Async function with fallback
result = await GracefulDegradation.with_fallback_async(
    async_risky_operation,
    fallback_value="default_value"
)
```

## ErrorCode Enum

All available error codes organized by category:

### File Errors
- `INVALID_PDF`: Corrupt or unsupported PDF format
- `FILE_TOO_LARGE`: File exceeds 100MB limit
- `UNSUPPORTED_FILE_TYPE`: File type not supported
- `FILE_CORRUPTED`: File is corrupted
- `FILE_NOT_FOUND`: File not found
- `DUPLICATE_FILE`: Duplicate file detected

### API Errors
- `RATE_LIMITED`: API rate limit exceeded (retryable)
- `TIMEOUT`: Request timeout (retryable)
- `API_ERROR`: General API error (retryable)
- `AUTH_ERROR`: Authentication failed
- `QUOTA_EXCEEDED`: API quota exceeded

### Database Errors
- `DB_ERROR`: General database error
- `DB_CONNECTION_ERROR`: Database connection failed (retryable)
- `DB_TRANSACTION_ERROR`: Transaction failed
- `RECORD_NOT_FOUND`: Record not found
- `DUPLICATE_RECORD`: Duplicate record

### Processing Errors
- `PARSING_ERROR`: Failed to parse content
- `GENERATION_ERROR`: Failed to generate content
- `VALIDATION_ERROR`: Validation failed
- `PROCESSING_TIMEOUT`: Processing timeout

### State Errors
- `DOCUMENT_NOT_READY`: Document not ready for operation
- `INVALID_STATE`: Invalid state for operation
- `OPERATION_NOT_ALLOWED`: Operation not allowed

### Generic Errors
- `INTERNAL_ERROR`: Internal server error
- `UNKNOWN_ERROR`: Unknown error
- `CONFIGURATION_ERROR`: Configuration error

## AppError Class

### Attributes

- `error_code` (ErrorCode): Standardized error code
- `message` (str): Human-readable error message
- `details` (dict): Additional error context
- `status_code` (int): HTTP status code (default: 500)
- `is_retryable` (bool): Whether operation can be retried (default: False)

### Methods

- `to_dict()`: Convert to dictionary for JSON serialization
- `__str__()`: String representation
- `__repr__()`: Detailed representation

### Example

```python
error = AppError(
    error_code=ErrorCode.RATE_LIMITED,
    message="Rate limit exceeded",
    details={"retry_after": 60},
    status_code=429,
    is_retryable=True
)

# Serialize to dict
error_dict = error.to_dict()
# {'error_code': 'RATE_LIMITED', 'message': 'Rate limit exceeded', 'details': {'retry_after': 60}}
```

## retry_with_backoff Decorator

Decorator for automatic retry with exponential backoff, supporting both sync and async functions.

### Parameters

- `max_retries` (int): Maximum retry attempts (default: 3)
- `initial_delay` (float): Initial delay in seconds (default: 1.0)
- `max_delay` (float): Maximum delay cap (default: 60.0)
- `exponential_base` (float): Exponential base (default: 2.0)
- `exceptions` (tuple): Exception types to catch (default: all Exception)
- `retryable_error_codes` (set): ErrorCode values to retry
- `on_retry` (Callable): Optional callback on retry

### Default Retryable Error Codes

- `ErrorCode.RATE_LIMITED`
- `ErrorCode.TIMEOUT`
- `ErrorCode.API_ERROR`
- `ErrorCode.DB_CONNECTION_ERROR`

### Exponential Backoff

Delays follow the formula: `min(initial_delay * (exponential_base ** attempt), max_delay)`

- Attempt 1: 1.0s
- Attempt 2: 2.0s
- Attempt 3: 4.0s
- Attempt 4: 8.0s
- Capped at max_delay

### Example

```python
@retry_with_backoff(
    max_retries=5,
    initial_delay=1.0,
    max_delay=30.0,
    retryable_error_codes={ErrorCode.RATE_LIMITED}
)
async def call_gemini_api(prompt: str):
    # API call implementation
    pass
```

### With Callback

```python
def on_retry_callback(exception: Exception, attempt: int, delay: float):
    logger.warning(f"Retry {attempt} after {delay}s: {exception}")

@retry_with_backoff(max_retries=3, on_retry=on_retry_callback)
def flaky_operation():
    # Your operation here
    pass
```

## Graceful Degradation

### with_fallback (Sync)

```python
def get_user_name():
    # Might fail
    return db.query_user_name()

wrapped = GracefulDegradation.with_fallback(
    get_user_name,
    fallback_value="Anonymous",
    exceptions=(DatabaseError,),
    log_errors=True
)

name = wrapped()  # Returns "Anonymous" on error
```

### with_fallback_async (Async)

```python
async def get_summary():
    # Might fail
    return await generate_summary()

result = await GracefulDegradation.with_fallback_async(
    get_summary,
    fallback_value="Summary unavailable",
    exceptions=(APIError,)
)
```

## HTTP Status Code Mapping

Automatic HTTP status codes based on error codes:

- **400 Bad Request**: INVALID_PDF, FILE_TOO_LARGE, VALIDATION_ERROR
- **401 Unauthorized**: AUTH_ERROR
- **404 Not Found**: FILE_NOT_FOUND, RECORD_NOT_FOUND
- **409 Conflict**: DUPLICATE_RECORD, DOCUMENT_NOT_READY
- **429 Too Many Requests**: RATE_LIMITED, QUOTA_EXCEEDED
- **500 Internal Server Error**: DB_ERROR, PARSING_ERROR, INTERNAL_ERROR
- **502 Bad Gateway**: API_ERROR
- **504 Gateway Timeout**: TIMEOUT, PROCESSING_TIMEOUT

```python
from src.utils.error_handler import get_status_code

status = get_status_code(ErrorCode.RATE_LIMITED)  # Returns 429
```

## Testing

Run tests with coverage:

```bash
cd backend
pytest tests/unit/test_error_handler.py -v --cov=src/utils
```

Current coverage: **89.10%** (37 tests, all passing)

## Integration with FastAPI

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.utils.error_handler import AppError, get_status_code

app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )
```

## Best Practices

1. **Use specific error codes**: Choose the most specific error code for your scenario
2. **Include details**: Add relevant context in the `details` dictionary
3. **Set is_retryable correctly**: Only mark truly retryable errors
4. **Log retry attempts**: Use `on_retry` callback for monitoring
5. **Test error paths**: Write tests for both success and error scenarios
6. **Document errors**: Document which errors your functions can raise

## See Also

- `src/utils/error_handler_examples.py` - Usage examples
- `tests/unit/test_error_handler.py` - Comprehensive test suite
- Repository constitution - Error handling guidelines
