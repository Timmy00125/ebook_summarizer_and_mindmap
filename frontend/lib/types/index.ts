/**
 * TypeScript interfaces for API types
 * Based on backend-api.yaml contract and data-model.md
 */

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Document upload and parsing status
 */
export enum DocumentStatus {
  UPLOADING = "uploading",
  PARSING = "parsing",
  READY = "ready",
  FAILED = "failed",
}

/**
 * Generation status for summaries and mindmaps
 */
export enum GenerationStatus {
  QUEUED = "queued",
  GENERATING = "generating",
  COMPLETE = "complete",
  FAILED = "failed",
}

/**
 * Health check status
 */
export enum HealthStatus {
  OK = "ok",
  DEGRADED = "degraded",
  ERROR = "error",
  RATE_LIMITED = "rate_limited",
}

// ============================================================================
// DOCUMENT TYPES
// ============================================================================

/**
 * PDF metadata extracted from document
 */
export interface DocumentMetadata {
  author?: string | null;
  title?: string | null;
  creation_date?: string | null;
}

/**
 * Document response (list view)
 */
export interface DocumentResponse {
  id: number;
  filename: string;
  file_size_bytes: number;
  page_count?: number | null;
  upload_status: DocumentStatus;
  error_message?: string | null;
  created_at: string;
  expires_at: string;
}

/**
 * Document detail response (includes summary and mindmap)
 */
export interface DocumentDetail extends DocumentResponse {
  metadata?: DocumentMetadata;
  summary?: SummaryResponse | null;
  mindmap?: MindmapResponse | null;
}

/**
 * Document list response with pagination
 */
export interface DocumentListResponse {
  total: number;
  documents: DocumentResponse[];
}

// ============================================================================
// SUMMARY TYPES
// ============================================================================

/**
 * Summary response
 */
export interface SummaryResponse {
  id: number;
  document_id: number;
  summary_text?: string | null;
  generation_status: GenerationStatus;
  error_message?: string | null;
  tokens_input?: number | null;
  tokens_output?: number | null;
  latency_ms?: number | null;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// MINDMAP TYPES
// ============================================================================

/**
 * Mindmap node structure (recursive)
 */
export interface MindmapNode {
  title: string;
  children: MindmapNode[];
}

/**
 * Mindmap response
 */
export interface MindmapResponse {
  id: number;
  document_id: number;
  mindmap_json?: MindmapNode | null;
  generation_status: GenerationStatus;
  error_message?: string | null;
  tokens_input?: number | null;
  tokens_output?: number | null;
  latency_ms?: number | null;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// ERROR TYPES
// ============================================================================

/**
 * Standard error codes returned by the API
 */
export enum ErrorCode {
  // File upload errors
  INVALID_PDF = "INVALID_PDF",
  FILE_TOO_LARGE = "FILE_TOO_LARGE",
  DUPLICATE_FILE = "DUPLICATE_FILE",
  INVALID_FILE_SIZE = "INVALID_FILE_SIZE",
  INVALID_MIME_TYPE = "INVALID_MIME_TYPE",
  INVALID_FILENAME = "INVALID_FILENAME",

  // Document processing errors
  DOCUMENT_NOT_READY = "DOCUMENT_NOT_READY",
  NO_TEXT = "NO_TEXT",

  // Generation errors
  RATE_LIMITED = "RATE_LIMITED",
  TIMEOUT = "TIMEOUT",
  
  // Mindmap validation errors
  MAX_DEPTH_EXCEEDED = "MAX_DEPTH_EXCEEDED",
  MISSING_TITLE = "MISSING_TITLE",
  MISSING_CHILDREN = "MISSING_CHILDREN",
  TOO_MANY_CHILDREN = "TOO_MANY_CHILDREN",

  // Database errors
  DB_ERROR = "DB_ERROR",

  // Auth errors
  AUTH_ERROR = "AUTH_ERROR",
  UNAUTHORIZED = "UNAUTHORIZED",

  // Generic errors
  VALIDATION_ERROR = "VALIDATION_ERROR",
  INTERNAL_ERROR = "INTERNAL_ERROR",
  NOT_FOUND = "NOT_FOUND",
}

/**
 * API error response
 */
export interface ApiError {
  error_code: string;
  detail: string;
  timestamp?: string;
  request_id?: string;
}

// ============================================================================
// API RESPONSE WRAPPERS
// ============================================================================

/**
 * Generic success response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  status: number;
}

/**
 * Generic error response wrapper
 */
export interface ApiErrorResponse {
  error: ApiError;
  status: number;
}

// ============================================================================
// HEALTH CHECK TYPES
// ============================================================================

/**
 * Health check response
 */
export interface HealthCheckResponse {
  status: HealthStatus;
  database: HealthStatus;
  gemini_api: HealthStatus;
  timestamp: string;
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

/**
 * Summary generation request body
 */
export interface GenerateSummaryRequest {
  maxTokens?: number;
}

/**
 * Document list query parameters
 */
export interface DocumentListParams {
  skip?: number;
  limit?: number;
  status?: DocumentStatus;
}

/**
 * Download format options
 */
export enum DownloadFormat {
  TXT = "txt",
  PDF = "pdf",
  MARKDOWN = "markdown",
  JSON = "json",
  PNG = "png",
  SVG = "svg",
}
