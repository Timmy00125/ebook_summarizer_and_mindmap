/**
 * Usage examples for errorFormatter utility
 * 
 * This file demonstrates how to use the error formatter in different scenarios.
 * These examples can be used as reference when integrating with API clients.
 */

import { formatError, getErrorMessage, isRetryableError, ErrorCode } from "./errorFormatter";

// Example 1: Format API error with error_code
export function exampleApiError() {
  const apiError = {
    error_code: "INVALID_PDF",
    message: "The file is not a valid PDF document",
    details: {},
  };

  const formatted = formatError(apiError);
  console.log(formatted);
  // Output: {
  //   title: "Invalid File",
  //   message: "The uploaded file is not a valid PDF",
  //   isRetryable: false
  // }
}

// Example 2: Format network error
export function exampleNetworkError() {
  const networkError = {
    code: "ERR_NETWORK",
    message: "Network Error",
    request: {},
    // no response property indicates network error
  };

  const formatted = formatError(networkError);
  console.log(formatted);
  // Output: {
  //   title: "Network Error",
  //   message: "Unable to connect to the server. Please check your internet connection and try again.",
  //   isRetryable: true
  // }
}

// Example 3: Format validation error with field details
export function exampleValidationError() {
  const validationError = {
    error_code: "VALIDATION_ERROR",
    message: "Validation failed",
    details: {
      filename: "Filename is required",
      size: "File size must be less than 100MB",
    },
  };

  const formatted = formatError(validationError);
  console.log(formatted);
  // Output: {
  //   title: "Validation Error",
  //   message: "Validation failed",
  //   details: [
  //     { field: "filename", message: "Filename is required" },
  //     { field: "size", message: "File size must be less than 100MB" }
  //   ],
  //   isRetryable: false
  // }
}

// Example 4: Format HTTP status error
export function exampleHttpError() {
  const httpError = {
    status: 429,
    statusText: "Too Many Requests",
  };

  const formatted = formatError(httpError);
  console.log(formatted);
  // Output: {
  //   title: "Too Many Requests",
  //   message: "Too many requests. Please wait a moment and try again.",
  //   isRetryable: true
  // }
}

// Example 5: Get specific error message
export function exampleGetErrorMessage() {
  const message = getErrorMessage(ErrorCode.FILE_TOO_LARGE);
  console.log(message);
  // Output: "File size exceeds 100MB limit"
}

// Example 6: Check if error is retryable
export function exampleIsRetryable() {
  const apiError = {
    error_code: "TIMEOUT",
    message: "Request timed out",
  };

  const canRetry = isRetryableError(apiError);
  console.log(canRetry);
  // Output: true
}

// Example 7: Usage in Axios interceptor
export function exampleAxiosInterceptor() {
  // This would be in your API client setup
  /*
  import axios from 'axios';
  import { formatError } from './errorFormatter';

  axios.interceptors.response.use(
    response => response,
    error => {
      // Format the error for display
      const formattedError = formatError(error.response?.data || error);
      
      // You can now use formattedError.message for display
      // and formattedError.isRetryable to decide retry logic
      
      return Promise.reject(formattedError);
    }
  );
  */
}

// Example 8: Usage in component error handling
export function exampleComponentUsage() {
  /*
  import { formatError } from '@/lib/utils/errorFormatter';

  async function uploadFile(file: File) {
    try {
      const response = await api.post('/documents', { file });
      return response.data;
    } catch (error) {
      const formatted = formatError(error);
      
      // Show user-friendly message
      toast.error(formatted.message);
      
      // Optionally show details
      if (formatted.details) {
        formatted.details.forEach(detail => {
          toast.error(`${detail.field}: ${detail.message}`);
        });
      }
      
      // Handle retry logic
      if (formatted.isRetryable) {
        // Show retry button
      }
    }
  }
  */
}
