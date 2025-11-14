# API Client Documentation

## Overview

The API client (`lib/services/api.ts`) provides a centralized, type-safe HTTP client for communicating with the backend API. It's built on Axios and includes:

- **Configuration**: Base URL, timeout, and debug mode from environment variables
- **Request Interceptor**: Adds authentication headers and logs requests in development
- **Response Interceptor**: Transforms responses and handles errors gracefully
- **Error Handling**: Converts backend error codes to user-friendly messages
- **Retry Logic**: Automatic retry with exponential backoff for network errors
- **TypeScript**: Full type safety with TypeScript definitions

## Installation

The API client is already installed and configured. No additional setup is required.

## Configuration

Set the following environment variables in `.env.local`:

```bash
# Backend API base URL (required)
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# API request timeout in milliseconds (optional, default: 30000)
NEXT_PUBLIC_API_TIMEOUT_MS=30000

# Enable verbose API logging in development (optional, default: false)
NEXT_PUBLIC_API_DEBUG=true

# API key for authentication (optional, for future use)
NEXT_PUBLIC_API_KEY=your-api-key
```

## Usage

### Basic Usage

```typescript
import { api } from '@/lib/services';

// GET request
const response = await api.get('/documents');
const documents = response.data;

// POST request
const newDocument = await api.post('/documents', {
  filename: 'example.pdf',
});

// PUT request
const updated = await api.put('/documents/1', {
  filename: 'new-name.pdf',
});

// DELETE request
await api.delete('/documents/1');
```

### Type-Safe Usage

```typescript
import { api } from '@/lib/services';
import { DocumentResponse, PaginatedResponse } from '@/lib/types';

// GET with types
const response = await api.get<PaginatedResponse<DocumentResponse>>('/documents');
const documents = response.data.documents; // Fully typed!

// POST with types
const document = await api.post<DocumentResponse>('/documents', formData);
console.log(document.data.filename); // Type-safe property access
```

### Error Handling

```typescript
import { api } from '@/lib/services';
import { ApiError, ErrorCode } from '@/lib/types';

try {
  const response = await api.get('/documents/999');
} catch (error) {
  if (error instanceof ApiError) {
    // Structured error with user-friendly message
    console.error('Error:', error.message);
    console.error('Code:', error.errorCode);
    console.error('Status:', error.statusCode);
    
    // Check specific error codes
    if (error.errorCode === ErrorCode.FILE_NOT_FOUND) {
      // Handle not found
    }
    
    // Check if error is retryable
    if (error.isRetryable) {
      // Error was automatically retried, still failed
    }
  } else {
    // Unexpected error
    console.error('Unexpected error:', error);
  }
}
```

### File Upload

```typescript
import { api } from '@/lib/services';
import { DocumentResponse } from '@/lib/types';

async function uploadFile(file: File): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<DocumentResponse>('/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}
```

## Features

### Request Interceptor

The request interceptor:
1. Adds authentication headers (X-API-Key) if available
2. Logs requests in development mode
3. Initializes retry configuration

### Response Interceptor

The response interceptor:
1. Logs successful responses in development mode
2. Transforms error responses to structured ApiError instances
3. Implements automatic retry with exponential backoff for retryable errors

### Retry Logic

The client automatically retries failed requests with exponential backoff when:
- Network errors occur (no response from server)
- Rate limiting errors (429)
- Timeout errors (408)
- Database connection errors
- General API errors

**Retry Configuration:**
- Maximum retries: 3
- Initial delay: 1 second
- Exponential backoff: delay × 2^(attempt - 1)
- Example delays: 1s, 2s, 4s

### Error Transformation

All errors are transformed to user-friendly messages:

| Backend Error Code | User-Friendly Message |
|-------------------|----------------------|
| INVALID_PDF | "The file you uploaded is not a valid PDF document. Please check the file and try again." |
| FILE_TOO_LARGE | "The file is too large. Maximum file size is 100MB." |
| RATE_LIMITED | "Too many requests. Please wait a moment and try again." |
| NETWORK_ERROR | "Unable to connect to the server. Please check your internet connection." |

See `lib/services/errorTransform.ts` for the complete list.

## Type Definitions

All API types are defined in `lib/types/api.ts`:

- `ErrorCode`: Enumeration of all error codes
- `ApiError`: Custom error class with structured information
- `DocumentResponse`: Document data structure
- `SummaryResponse`: Summary data structure
- `MindmapResponse`: Mindmap data structure
- `HealthCheckResponse`: Health check response
- And more...

## Examples

See `lib/services/apiExamples.ts` for complete, working examples of all common operations.

## Testing

To test the API client in your application:

1. Set up the backend server:
   ```bash
   cd backend
   uvicorn src.main:app --reload
   ```

2. Configure the frontend environment:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your settings
   ```

3. Use the API client in your components:
   ```typescript
   import { checkHealth } from '@/lib/services/apiExamples';
   
   const health = await checkHealth();
   console.log('API Status:', health.status);
   ```

## Debugging

To enable debug logging:

```bash
# In .env.local
NEXT_PUBLIC_API_DEBUG=true
```

This will log:
- All outgoing requests with headers and parameters
- All responses with status and data
- All errors with details
- Retry attempts with delay information

## Architecture

```
lib/
├── types/
│   ├── api.ts           # TypeScript type definitions
│   └── index.ts         # Type exports
└── services/
    ├── api.ts           # Main Axios client with interceptors
    ├── errorTransform.ts # Error transformation utilities
    ├── apiExamples.ts   # Usage examples
    └── index.ts         # Service exports
```

## Dependencies

- `axios` ^1.13.2: HTTP client library
- TypeScript types included in axios package

## Future Enhancements

- [ ] Request/response caching
- [ ] Request deduplication
- [ ] Progress tracking for file uploads
- [ ] Offline queue for failed requests
- [ ] WebSocket support for real-time updates
- [ ] Request cancellation support
