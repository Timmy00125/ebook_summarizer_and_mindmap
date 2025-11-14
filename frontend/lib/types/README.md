# TypeScript API Types

This directory contains TypeScript interfaces for all API types used in the frontend application.

## Overview

The `index.ts` file defines comprehensive TypeScript types based on:
- `backend-api.yaml` - OpenAPI contract
- `data-model.md` - Database schema and business logic

## Usage

```typescript
import {
  DocumentResponse,
  DocumentStatus,
  SummaryResponse,
  GenerationStatus,
  ApiError,
  ApiResponse,
} from '@/lib/types';

// Example: Handling document upload response
const handleUploadResponse = (response: ApiResponse<DocumentResponse>) => {
  const { data } = response;
  
  if (data.upload_status === DocumentStatus.READY) {
    console.log('Document ready:', data.filename);
  }
};

// Example: Checking summary generation status
const checkSummaryStatus = (summary: SummaryResponse) => {
  switch (summary.generation_status) {
    case GenerationStatus.COMPLETE:
      console.log('Summary:', summary.summary_text);
      break;
    case GenerationStatus.FAILED:
      console.error('Error:', summary.error_message);
      break;
    case GenerationStatus.GENERATING:
      console.log('Still generating...');
      break;
  }
};

// Example: Error handling
const handleApiError = (error: ApiError) => {
  console.error(`Error ${error.error_code}: ${error.detail}`);
  if (error.request_id) {
    console.log('Request ID:', error.request_id);
  }
};
```

## Type Categories

### Enums
- **DocumentStatus**: Upload and parsing states
- **GenerationStatus**: AI generation states
- **HealthStatus**: Service health states
- **ErrorCode**: Standard error codes
- **DownloadFormat**: File download formats

### Document Types
- **DocumentResponse**: Basic document information
- **DocumentDetail**: Extended document with relations
- **DocumentMetadata**: PDF metadata
- **DocumentListResponse**: Paginated list

### Generation Types
- **SummaryResponse**: AI-generated summary
- **MindmapResponse**: Hierarchical mindmap
- **MindmapNode**: Recursive node structure

### API Types
- **ApiResponse<T>**: Generic success wrapper
- **ApiError**: Error details
- **ApiErrorResponse**: Error wrapper
- **HealthCheckResponse**: System health

### Request Types
- **GenerateSummaryRequest**: Summary options
- **DocumentListParams**: List filters

## Type Safety

All types include:
- Proper nullable fields (`field?: type | null`)
- Comprehensive JSDoc documentation
- Enum constraints for status fields
- Recursive types for hierarchical data

## Validation

Types are validated against:
- ✅ Backend API contract (OpenAPI spec)
- ✅ Database schema (data-model.md)
- ✅ TypeScript compiler (strict mode)
- ✅ ESLint rules
