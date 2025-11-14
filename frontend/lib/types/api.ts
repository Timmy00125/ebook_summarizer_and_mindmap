/**
 * Type definitions for API requests and responses.
 * 
 * These types align with the backend API specification in:
 * specs/001-pdf-summary-mindmap/contracts/backend-api.yaml
 */

/**
 * Error codes matching backend ErrorCode enum.
 * Used for consistent error handling across the application.
 */
export enum ErrorCode {
  // File upload and validation errors
  INVALID_PDF = 'INVALID_PDF',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  UNSUPPORTED_FILE_TYPE = 'UNSUPPORTED_FILE_TYPE',
  FILE_CORRUPTED = 'FILE_CORRUPTED',
  FILE_NOT_FOUND = 'FILE_NOT_FOUND',
  DUPLICATE_FILE = 'DUPLICATE_FILE',

  // API and rate limiting errors
  RATE_LIMITED = 'RATE_LIMITED',
  TIMEOUT = 'TIMEOUT',
  API_ERROR = 'API_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  QUOTA_EXCEEDED = 'QUOTA_EXCEEDED',

  // Database errors
  DB_ERROR = 'DB_ERROR',
  DB_CONNECTION_ERROR = 'DB_CONNECTION_ERROR',
  DB_TRANSACTION_ERROR = 'DB_TRANSACTION_ERROR',
  RECORD_NOT_FOUND = 'RECORD_NOT_FOUND',
  DUPLICATE_RECORD = 'DUPLICATE_RECORD',

  // Processing errors
  PARSING_ERROR = 'PARSING_ERROR',
  GENERATION_ERROR = 'GENERATION_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  PROCESSING_TIMEOUT = 'PROCESSING_TIMEOUT',

  // Document state errors
  DOCUMENT_NOT_READY = 'DOCUMENT_NOT_READY',
  INVALID_STATE = 'INVALID_STATE',
  OPERATION_NOT_ALLOWED = 'OPERATION_NOT_ALLOWED',

  // Generic errors
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
  CONFIGURATION_ERROR = 'CONFIGURATION_ERROR',

  // Network errors (frontend-only)
  NETWORK_ERROR = 'NETWORK_ERROR',
}

/**
 * API error response structure from backend.
 */
export interface ApiErrorResponse {
  error_code: string;
  detail: string;
  timestamp?: string;
  request_id?: string;
}

/**
 * Custom error class for API errors with structured information.
 */
export class ApiError extends Error {
  public readonly errorCode: ErrorCode;
  public readonly statusCode: number;
  public readonly timestamp?: string;
  public readonly requestId?: string;
  public readonly isRetryable: boolean;

  constructor(
    errorCode: ErrorCode,
    message: string,
    statusCode: number = 500,
    options?: {
      timestamp?: string;
      requestId?: string;
      isRetryable?: boolean;
    }
  ) {
    super(message);
    this.name = 'ApiError';
    this.errorCode = errorCode;
    this.statusCode = statusCode;
    this.timestamp = options?.timestamp;
    this.requestId = options?.requestId;
    this.isRetryable = options?.isRetryable ?? false;

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
  }

  /**
   * Convert to plain object for logging or serialization.
   */
  toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      errorCode: this.errorCode,
      message: this.message,
      statusCode: this.statusCode,
      timestamp: this.timestamp,
      requestId: this.requestId,
      isRetryable: this.isRetryable,
    };
  }
}

/**
 * Document upload status enum.
 */
export enum UploadStatus {
  UPLOADING = 'uploading',
  PARSING = 'parsing',
  READY = 'ready',
  FAILED = 'failed',
}

/**
 * Generation status for summaries and mindmaps.
 */
export enum GenerationStatus {
  QUEUED = 'queued',
  GENERATING = 'generating',
  COMPLETE = 'complete',
  FAILED = 'failed',
}

/**
 * Document response from API.
 */
export interface DocumentResponse {
  id: number;
  filename: string;
  file_size_bytes: number;
  page_count?: number;
  upload_status: UploadStatus;
  error_message?: string;
  created_at: string;
  expires_at: string;
}

/**
 * Document detail with related data.
 */
export interface DocumentDetail extends DocumentResponse {
  metadata?: {
    author?: string;
    title?: string;
    creation_date?: string;
  };
  summary?: SummaryResponse;
  mindmap?: MindmapResponse;
}

/**
 * Summary response from API.
 */
export interface SummaryResponse {
  id: number;
  document_id: number;
  summary_text?: string;
  generation_status: GenerationStatus;
  error_message?: string;
  tokens_input?: number;
  tokens_output?: number;
  cost_usd?: number;
  latency_ms?: number;
  created_at: string;
  updated_at: string;
}

/**
 * Mindmap node structure.
 */
export interface MindmapNode {
  title: string;
  children?: MindmapNode[];
}

/**
 * Mindmap response from API.
 */
export interface MindmapResponse {
  id: number;
  document_id: number;
  structure?: MindmapNode;
  generation_status: GenerationStatus;
  error_message?: string;
  tokens_input?: number;
  tokens_output?: number;
  latency_ms?: number;
  created_at: string;
  updated_at: string;
}

/**
 * Health check response.
 */
export interface HealthCheckResponse {
  status: 'ok' | 'degraded';
  database: 'ok' | 'error';
  gemini_api: 'ok' | 'error' | 'rate_limited';
  timestamp: string;
}

/**
 * Paginated list response.
 */
export interface PaginatedResponse<T> {
  total: number;
  documents: T[];
}
