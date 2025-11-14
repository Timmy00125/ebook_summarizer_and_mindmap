/**
 * Error formatter utility for converting API errors into user-friendly messages.
 * 
 * This module provides:
 * - Error code to message mapping
 * - Network error handling
 * - Validation error formatting
 * - Internationalization structure (future-ready)
 * - Fallback messages for unknown errors
 */

/**
 * Error codes matching backend ErrorCode enum
 */
export enum ErrorCode {
  // File upload and validation errors
  INVALID_PDF = "INVALID_PDF",
  FILE_TOO_LARGE = "FILE_TOO_LARGE",
  UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE",
  FILE_CORRUPTED = "FILE_CORRUPTED",
  FILE_NOT_FOUND = "FILE_NOT_FOUND",
  DUPLICATE_FILE = "DUPLICATE_FILE",

  // API and rate limiting errors
  RATE_LIMITED = "RATE_LIMITED",
  TIMEOUT = "TIMEOUT",
  API_ERROR = "API_ERROR",
  AUTH_ERROR = "AUTH_ERROR",
  QUOTA_EXCEEDED = "QUOTA_EXCEEDED",

  // Database errors
  DB_ERROR = "DB_ERROR",
  DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR",
  DB_TRANSACTION_ERROR = "DB_TRANSACTION_ERROR",
  RECORD_NOT_FOUND = "RECORD_NOT_FOUND",
  DUPLICATE_RECORD = "DUPLICATE_RECORD",

  // Processing errors
  PARSING_ERROR = "PARSING_ERROR",
  GENERATION_ERROR = "GENERATION_ERROR",
  VALIDATION_ERROR = "VALIDATION_ERROR",
  PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT",

  // Document state errors
  DOCUMENT_NOT_READY = "DOCUMENT_NOT_READY",
  INVALID_STATE = "INVALID_STATE",
  OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED",

  // Generic errors
  INTERNAL_ERROR = "INTERNAL_ERROR",
  UNKNOWN_ERROR = "UNKNOWN_ERROR",
  CONFIGURATION_ERROR = "CONFIGURATION_ERROR",
}

/**
 * API error structure from backend
 */
export interface ApiError {
  error_code?: string;
  message?: string;
  details?: Record<string, unknown>;
}

/**
 * Validation error with field-specific messages
 */
export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Formatted error result
 */
export interface FormattedError {
  message: string;
  title?: string;
  details?: ValidationError[];
  isRetryable?: boolean;
}

/**
 * Error message mappings (future: can be replaced with i18n keys)
 */
const ERROR_MESSAGES: Record<string, { message: string; title?: string; isRetryable?: boolean }> = {
  // File upload and validation errors
  [ErrorCode.INVALID_PDF]: {
    title: "Invalid File",
    message: "The uploaded file is not a valid PDF",
    isRetryable: false,
  },
  [ErrorCode.FILE_TOO_LARGE]: {
    title: "File Too Large",
    message: "File size exceeds 100MB limit",
    isRetryable: false,
  },
  [ErrorCode.UNSUPPORTED_FILE_TYPE]: {
    title: "Unsupported File Type",
    message: "Please upload a PDF file",
    isRetryable: false,
  },
  [ErrorCode.FILE_CORRUPTED]: {
    title: "Corrupted File",
    message: "The uploaded file appears to be corrupted",
    isRetryable: false,
  },
  [ErrorCode.FILE_NOT_FOUND]: {
    title: "File Not Found",
    message: "The requested file was not found",
    isRetryable: false,
  },
  [ErrorCode.DUPLICATE_FILE]: {
    title: "Duplicate File",
    message: "This file has already been uploaded",
    isRetryable: false,
  },

  // API and rate limiting errors
  [ErrorCode.RATE_LIMITED]: {
    title: "Too Many Requests",
    message: "Too many requests, please try again later",
    isRetryable: true,
  },
  [ErrorCode.TIMEOUT]: {
    title: "Request Timeout",
    message: "Request timed out, please try again",
    isRetryable: true,
  },
  [ErrorCode.API_ERROR]: {
    title: "API Error",
    message: "An error occurred while communicating with the server",
    isRetryable: true,
  },
  [ErrorCode.AUTH_ERROR]: {
    title: "Authentication Error",
    message: "Authentication failed, please sign in again",
    isRetryable: false,
  },
  [ErrorCode.QUOTA_EXCEEDED]: {
    title: "Quota Exceeded",
    message: "Your usage quota has been exceeded",
    isRetryable: false,
  },

  // Database errors
  [ErrorCode.DB_ERROR]: {
    title: "Database Error",
    message: "A database error occurred, please try again",
    isRetryable: true,
  },
  [ErrorCode.DB_CONNECTION_ERROR]: {
    title: "Connection Error",
    message: "Failed to connect to the database",
    isRetryable: true,
  },
  [ErrorCode.DB_TRANSACTION_ERROR]: {
    title: "Transaction Error",
    message: "A database transaction error occurred",
    isRetryable: true,
  },
  [ErrorCode.RECORD_NOT_FOUND]: {
    title: "Not Found",
    message: "The requested record was not found",
    isRetryable: false,
  },
  [ErrorCode.DUPLICATE_RECORD]: {
    title: "Duplicate Record",
    message: "A record with this information already exists",
    isRetryable: false,
  },

  // Processing errors
  [ErrorCode.PARSING_ERROR]: {
    title: "Parsing Error",
    message: "Failed to parse the document",
    isRetryable: false,
  },
  [ErrorCode.GENERATION_ERROR]: {
    title: "Generation Error",
    message: "Failed to generate content",
    isRetryable: true,
  },
  [ErrorCode.VALIDATION_ERROR]: {
    title: "Validation Error",
    message: "The provided data is invalid",
    isRetryable: false,
  },
  [ErrorCode.PROCESSING_TIMEOUT]: {
    title: "Processing Timeout",
    message: "Processing took too long, please try again",
    isRetryable: true,
  },

  // Document state errors
  [ErrorCode.DOCUMENT_NOT_READY]: {
    title: "Document Not Ready",
    message: "The document is still being processed",
    isRetryable: true,
  },
  [ErrorCode.INVALID_STATE]: {
    title: "Invalid State",
    message: "The operation cannot be performed in the current state",
    isRetryable: false,
  },
  [ErrorCode.OPERATION_NOT_ALLOWED]: {
    title: "Operation Not Allowed",
    message: "This operation is not allowed",
    isRetryable: false,
  },

  // Generic errors
  [ErrorCode.INTERNAL_ERROR]: {
    title: "Internal Error",
    message: "An internal error occurred, please try again",
    isRetryable: true,
  },
  [ErrorCode.UNKNOWN_ERROR]: {
    title: "Unknown Error",
    message: "An unknown error occurred, please try again",
    isRetryable: true,
  },
  [ErrorCode.CONFIGURATION_ERROR]: {
    title: "Configuration Error",
    message: "A configuration error occurred",
    isRetryable: false,
  },
};

/**
 * Format an API error into a user-friendly message
 * 
 * @param error - The error object from the API or network
 * @returns Formatted error with user-friendly message
 */
export function formatError(error: unknown): FormattedError {
  // Handle network errors (no response from server)
  if (isNetworkError(error)) {
    return {
      title: "Network Error",
      message: "Unable to connect to the server. Please check your internet connection and try again.",
      isRetryable: true,
    };
  }

  // Handle API errors with error_code
  if (isApiError(error)) {
    const errorCode = error.error_code;
    
    if (errorCode && ERROR_MESSAGES[errorCode]) {
      const errorConfig = ERROR_MESSAGES[errorCode];
      
      // Handle validation errors with field details
      if (errorCode === ErrorCode.VALIDATION_ERROR && error.details) {
        return {
          ...errorConfig,
          details: formatValidationErrors(error.details),
        };
      }

      return {
        title: errorConfig.title,
        message: error.message || errorConfig.message,
        isRetryable: errorConfig.isRetryable,
      };
    }

    // Return backend message if no mapping exists
    if (error.message) {
      return {
        message: error.message,
        isRetryable: false,
      };
    }
  }

  // Handle HTTP status codes
  if (isHttpError(error)) {
    return formatHttpError(error as { status: number; statusText?: string });
  }

  // Fallback for unknown errors
  return {
    title: "Error",
    message: "An unexpected error occurred. Please try again.",
    isRetryable: true,
  };
}

/**
 * Check if error is a network error (no response)
 */
function isNetworkError(error: unknown): boolean {
  if (typeof error === "object" && error !== null) {
    const err = error as { code?: string; message?: string; request?: unknown; response?: unknown };
    // Axios network error detection
    return (
      (err.code === "ERR_NETWORK" || err.code === "ECONNREFUSED" || err.message?.includes("Network Error")) &&
      err.request !== undefined &&
      err.response === undefined
    );
  }
  return false;
}

/**
 * Check if error is an API error with error_code
 */
function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === "object" &&
    error !== null &&
    ("error_code" in error || "message" in error)
  );
}

/**
 * Check if error has HTTP status information
 */
function isHttpError(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    typeof (error as { status: unknown }).status === "number"
  );
}

/**
 * Format HTTP errors based on status code
 */
function formatHttpError(error: { status: number; statusText?: string }): FormattedError {
  const statusMessages: Record<number, FormattedError> = {
    400: {
      title: "Bad Request",
      message: "The request was invalid. Please check your input and try again.",
      isRetryable: false,
    },
    401: {
      title: "Unauthorized",
      message: "You need to sign in to access this resource.",
      isRetryable: false,
    },
    403: {
      title: "Forbidden",
      message: "You don't have permission to access this resource.",
      isRetryable: false,
    },
    404: {
      title: "Not Found",
      message: "The requested resource was not found.",
      isRetryable: false,
    },
    409: {
      title: "Conflict",
      message: "The request conflicts with the current state of the resource.",
      isRetryable: false,
    },
    429: {
      title: "Too Many Requests",
      message: "Too many requests. Please wait a moment and try again.",
      isRetryable: true,
    },
    500: {
      title: "Server Error",
      message: "The server encountered an error. Please try again later.",
      isRetryable: true,
    },
    502: {
      title: "Bad Gateway",
      message: "The server is temporarily unavailable. Please try again later.",
      isRetryable: true,
    },
    503: {
      title: "Service Unavailable",
      message: "The service is temporarily unavailable. Please try again later.",
      isRetryable: true,
    },
    504: {
      title: "Gateway Timeout",
      message: "The request took too long to complete. Please try again.",
      isRetryable: true,
    },
  };

  const formattedError = statusMessages[error.status];
  
  if (formattedError) {
    return formattedError;
  }

  // Default for unknown status codes
  return {
    title: "Error",
    message: error.statusText || "An error occurred. Please try again.",
    isRetryable: error.status >= 500,
  };
}

/**
 * Format validation errors from API response details
 */
function formatValidationErrors(details: Record<string, unknown>): ValidationError[] {
  const validationErrors: ValidationError[] = [];

  // Handle various validation error formats
  if (Array.isArray(details)) {
    // Array of validation errors
    details.forEach((detail) => {
      if (typeof detail === "object" && detail !== null) {
        const error = detail as Record<string, unknown>;
        validationErrors.push({
          field: String(error.field || error.loc?.[1] || "unknown"),
          message: String(error.message || error.msg || "Invalid value"),
        });
      }
    });
  } else if (typeof details === "object") {
    // Object with field keys
    Object.entries(details).forEach(([field, value]) => {
      if (typeof value === "string") {
        validationErrors.push({ field, message: value });
      } else if (Array.isArray(value) && value.length > 0) {
        validationErrors.push({ field, message: String(value[0]) });
      }
    });
  }

  return validationErrors;
}

/**
 * Get a user-friendly message for a specific error code
 * 
 * @param errorCode - The error code to get message for
 * @returns User-friendly error message
 */
export function getErrorMessage(errorCode: string): string {
  const errorConfig = ERROR_MESSAGES[errorCode];
  return errorConfig?.message || "An error occurred";
}

/**
 * Check if an error is retryable
 * 
 * @param error - The error to check
 * @returns Whether the error is retryable
 */
export function isRetryableError(error: unknown): boolean {
  const formatted = formatError(error);
  return formatted.isRetryable || false;
}
