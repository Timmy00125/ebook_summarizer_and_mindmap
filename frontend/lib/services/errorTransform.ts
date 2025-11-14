/**
 * Error transformation utilities for API errors.
 * Converts backend error codes to user-friendly messages.
 */

import { ApiError, ApiErrorResponse, ErrorCode } from '@/lib/types/api';

/**
 * User-friendly error messages for each error code.
 * These messages are displayed to end users.
 */
const ERROR_MESSAGES: Record<ErrorCode, string> = {
  // File upload and validation errors
  [ErrorCode.INVALID_PDF]: 'The file you uploaded is not a valid PDF document. Please check the file and try again.',
  [ErrorCode.FILE_TOO_LARGE]: 'The file is too large. Maximum file size is 100MB.',
  [ErrorCode.UNSUPPORTED_FILE_TYPE]: 'This file type is not supported. Please upload a PDF document.',
  [ErrorCode.FILE_CORRUPTED]: 'The PDF file appears to be corrupted. Please try uploading a different file.',
  [ErrorCode.FILE_NOT_FOUND]: 'The requested document could not be found. It may have been deleted.',
  [ErrorCode.DUPLICATE_FILE]: 'This file has already been uploaded.',

  // API and rate limiting errors
  [ErrorCode.RATE_LIMITED]: 'Too many requests. Please wait a moment and try again.',
  [ErrorCode.TIMEOUT]: 'The request took too long to complete. Please try again.',
  [ErrorCode.API_ERROR]: 'An error occurred while communicating with the server. Please try again.',
  [ErrorCode.AUTH_ERROR]: 'Authentication failed. Please check your credentials.',
  [ErrorCode.QUOTA_EXCEEDED]: 'API quota exceeded. Please try again later.',

  // Database errors
  [ErrorCode.DB_ERROR]: 'A database error occurred. Please try again later.',
  [ErrorCode.DB_CONNECTION_ERROR]: 'Unable to connect to the database. Please try again later.',
  [ErrorCode.DB_TRANSACTION_ERROR]: 'A database transaction error occurred. Please try again.',
  [ErrorCode.RECORD_NOT_FOUND]: 'The requested record was not found.',
  [ErrorCode.DUPLICATE_RECORD]: 'This record already exists.',

  // Processing errors
  [ErrorCode.PARSING_ERROR]: 'Unable to parse the document. The PDF may be corrupted or use unsupported features.',
  [ErrorCode.GENERATION_ERROR]: 'Failed to generate the requested content. Please try again.',
  [ErrorCode.VALIDATION_ERROR]: 'The request contains invalid data. Please check your input.',
  [ErrorCode.PROCESSING_TIMEOUT]: 'Processing took too long and was cancelled. Please try again.',

  // Document state errors
  [ErrorCode.DOCUMENT_NOT_READY]: 'The document is still being processed. Please wait and try again.',
  [ErrorCode.INVALID_STATE]: 'The document is not in a valid state for this operation.',
  [ErrorCode.OPERATION_NOT_ALLOWED]: 'This operation is not allowed for this document.',

  // Generic errors
  [ErrorCode.INTERNAL_ERROR]: 'An internal server error occurred. Please try again later.',
  [ErrorCode.UNKNOWN_ERROR]: 'An unexpected error occurred. Please try again.',
  [ErrorCode.CONFIGURATION_ERROR]: 'A configuration error occurred. Please contact support.',

  // Network errors (frontend-only)
  [ErrorCode.NETWORK_ERROR]: 'Unable to connect to the server. Please check your internet connection.',
};

/**
 * Determines if an error code represents a retryable error.
 * 
 * @param errorCode - The error code to check
 * @returns True if the error is retryable
 */
export function isRetryableError(errorCode: ErrorCode): boolean {
  const retryableErrors: ErrorCode[] = [
    ErrorCode.NETWORK_ERROR,
    ErrorCode.TIMEOUT,
    ErrorCode.RATE_LIMITED,
    ErrorCode.DB_CONNECTION_ERROR,
    ErrorCode.API_ERROR,
  ];

  return retryableErrors.includes(errorCode);
}

/**
 * Maps HTTP status codes to error codes.
 * 
 * @param statusCode - HTTP status code
 * @returns Appropriate ErrorCode
 */
function mapStatusCodeToErrorCode(statusCode: number): ErrorCode {
  switch (statusCode) {
    case 401:
    case 403:
      return ErrorCode.AUTH_ERROR;
    case 404:
      return ErrorCode.FILE_NOT_FOUND;
    case 408:
      return ErrorCode.TIMEOUT;
    case 413:
      return ErrorCode.FILE_TOO_LARGE;
    case 429:
      return ErrorCode.RATE_LIMITED;
    case 500:
    case 502:
    case 503:
    case 504:
      return ErrorCode.INTERNAL_ERROR;
    default:
      return ErrorCode.UNKNOWN_ERROR;
  }
}

/**
 * Transforms an API error response into an ApiError instance.
 * 
 * @param response - The error response from the backend
 * @param statusCode - HTTP status code
 * @returns ApiError instance with user-friendly message
 */
export function transformErrorResponse(
  response: ApiErrorResponse | undefined,
  statusCode: number
): ApiError {
  // If we have a structured error response from backend
  if (response?.error_code) {
    const errorCode = response.error_code as ErrorCode;
    const message = ERROR_MESSAGES[errorCode] || response.detail || 'An error occurred';
    
    return new ApiError(errorCode, message, statusCode, {
      timestamp: response.timestamp,
      requestId: response.request_id,
      isRetryable: isRetryableError(errorCode),
    });
  }

  // Fallback to status code mapping
  const errorCode = mapStatusCodeToErrorCode(statusCode);
  const message = ERROR_MESSAGES[errorCode];

  return new ApiError(errorCode, message, statusCode, {
    isRetryable: isRetryableError(errorCode),
  });
}

/**
 * Transforms network errors into ApiError instances.
 * 
 * @param _error - The network error (currently unused, may be used for additional context in future)
 * @returns ApiError instance
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function transformNetworkError(_error: Error): ApiError {
  return new ApiError(
    ErrorCode.NETWORK_ERROR,
    ERROR_MESSAGES[ErrorCode.NETWORK_ERROR],
    0,
    {
      isRetryable: true,
    }
  );
}

/**
 * Gets a user-friendly error message for an error code.
 * 
 * @param errorCode - The error code
 * @returns User-friendly error message
 */
export function getErrorMessage(errorCode: ErrorCode): string {
  return ERROR_MESSAGES[errorCode] || ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR];
}
