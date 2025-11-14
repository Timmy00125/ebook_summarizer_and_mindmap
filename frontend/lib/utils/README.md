# Error Formatter Utility

A comprehensive error formatting utility for converting API errors, network errors, and HTTP status codes into user-friendly messages.

## Features

- ✅ **Error Code Mappings**: All backend error codes mapped to user-friendly messages
- ✅ **Network Error Handling**: Detects and formats network connectivity errors
- ✅ **HTTP Status Codes**: Handles all common HTTP status codes (400, 401, 404, 429, 500, etc.)
- ✅ **Validation Errors**: Formats field-specific validation errors
- ✅ **Fallback Messages**: Provides default messages for unknown errors
- ✅ **Retry Detection**: Each error includes `isRetryable` flag
- ✅ **i18n-Ready**: Structure supports future internationalization

## Usage

### Basic Error Formatting

```typescript
import { formatError } from '@/lib/utils/errorFormatter';

// Format any error
const error = await apiCall().catch(e => e);
const formatted = formatError(error);

console.log(formatted.message); // User-friendly message
console.log(formatted.title);   // Error title (optional)
console.log(formatted.isRetryable); // Whether error can be retried
```

### Get Specific Error Message

```typescript
import { getErrorMessage, ErrorCode } from '@/lib/utils/errorFormatter';

const message = getErrorMessage(ErrorCode.FILE_TOO_LARGE);
// Returns: "File size exceeds 100MB limit"
```

### Check if Error is Retryable

```typescript
import { isRetryableError } from '@/lib/utils/errorFormatter';

const canRetry = isRetryableError(error);
if (canRetry) {
  // Show retry button
}
```

### Integration with Axios

```typescript
import axios from 'axios';
import { formatError } from '@/lib/utils/errorFormatter';

// Add response interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    const formatted = formatError(error.response?.data || error);
    return Promise.reject(formatted);
  }
);
```

### Component Usage

```typescript
import { formatError } from '@/lib/utils/errorFormatter';

async function handleUpload(file: File) {
  try {
    await uploadDocument(file);
  } catch (error) {
    const { message, details, isRetryable } = formatError(error);
    
    // Show main error message
    showToast(message, 'error');
    
    // Show validation details if present
    details?.forEach(detail => {
      showToast(`${detail.field}: ${detail.message}`, 'warning');
    });
    
    // Handle retry
    if (isRetryable) {
      setShowRetryButton(true);
    }
  }
}
```

## Error Code Mappings

| Error Code | User Message | Retryable |
|------------|-------------|-----------|
| `INVALID_PDF` | "The uploaded file is not a valid PDF" | No |
| `FILE_TOO_LARGE` | "File size exceeds 100MB limit" | No |
| `RATE_LIMITED` | "Too many requests, please try again later" | Yes |
| `TIMEOUT` | "Request timed out, please try again" | Yes |
| `DB_ERROR` | "A database error occurred, please try again" | Yes |
| `VALIDATION_ERROR` | "The provided data is invalid" | No |
| `NETWORK_ERROR` | "Unable to connect to the server..." | Yes |
| `INTERNAL_ERROR` | "An internal error occurred, please try again" | Yes |
| And many more... | See full list in errorFormatter.ts | - |

## HTTP Status Code Handling

The utility automatically handles HTTP status codes:

- **400 Bad Request**: "The request was invalid..."
- **401 Unauthorized**: "You need to sign in..."
- **403 Forbidden**: "You don't have permission..."
- **404 Not Found**: "The requested resource was not found"
- **429 Too Many Requests**: "Too many requests..."
- **500 Internal Server Error**: "The server encountered an error..."
- **502 Bad Gateway**: "The server is temporarily unavailable..."
- **503 Service Unavailable**: "The service is temporarily unavailable..."
- **504 Gateway Timeout**: "The request took too long..."

## Network Error Detection

The utility automatically detects network errors:

```typescript
// These are detected as network errors:
// - error.code === "ERR_NETWORK"
// - error.code === "ECONNREFUSED"
// - error.message includes "Network Error"
// - error.request exists but error.response is undefined
```

## Validation Error Formatting

Validation errors with field details are automatically formatted:

```typescript
// API returns:
{
  error_code: "VALIDATION_ERROR",
  details: {
    email: "Invalid email format",
    password: "Password must be at least 8 characters"
  }
}

// Formatted result:
{
  title: "Validation Error",
  message: "The provided data is invalid",
  details: [
    { field: "email", message: "Invalid email format" },
    { field: "password", message: "Password must be at least 8 characters" }
  ],
  isRetryable: false
}
```

## TypeScript Types

```typescript
export enum ErrorCode {
  INVALID_PDF = "INVALID_PDF",
  FILE_TOO_LARGE = "FILE_TOO_LARGE",
  RATE_LIMITED = "RATE_LIMITED",
  // ... and more
}

export interface ApiError {
  error_code?: string;
  message?: string;
  details?: Record<string, unknown>;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface FormattedError {
  message: string;
  title?: string;
  details?: ValidationError[];
  isRetryable?: boolean;
}
```

## Future Enhancements

The utility is designed to support future internationalization:

```typescript
// Future i18n integration:
const ERROR_MESSAGES = {
  [ErrorCode.INVALID_PDF]: {
    title: t('errors.invalid_pdf.title'),
    message: t('errors.invalid_pdf.message'),
    isRetryable: false,
  },
  // ...
};
```

## Testing

See `errorFormatter.examples.ts` for comprehensive usage examples.

## References

- Backend error codes: `backend/src/utils/error_handler.py`
- Spec document: `specs/001-pdf-summary-mindmap/spec.md`
- Task: T021 - Phase 2 Frontend Foundation
