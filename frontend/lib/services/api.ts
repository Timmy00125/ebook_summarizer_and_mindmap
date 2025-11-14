/**
 * Axios API client with interceptors for centralized HTTP communication.
 * 
 * Features:
 * - Configurable base URL and timeout from environment
 * - Request interceptor: adds auth headers, logs requests in dev mode
 * - Response interceptor: transforms responses, handles errors
 * - Automatic retry with exponential backoff for network errors
 * - User-friendly error messages
 * 
 * Usage:
 * ```typescript
 * import apiClient from '@/lib/services/api';
 * 
 * const response = await apiClient.get('/documents');
 * ```
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

import { ApiError, ApiErrorResponse } from '@/lib/types/api';

import { transformErrorResponse, transformNetworkError } from './errorTransform';

// ============================================================================
// CONFIGURATION
// ============================================================================

/**
 * API client configuration from environment variables.
 */
const config = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT_MS || '30000', 10),
  debug: process.env.NEXT_PUBLIC_API_DEBUG === 'true',
  maxRetries: 3,
  retryDelay: 1000, // Initial retry delay in milliseconds
};

/**
 * Retry configuration for exponential backoff.
 */
interface RetryConfig {
  retries: number;
  retryDelay: number;
}

// Add retry config to Axios request config
declare module 'axios' {
  export interface AxiosRequestConfig {
    _retry?: RetryConfig;
  }
}

// ============================================================================
// AXIOS INSTANCE
// ============================================================================

/**
 * Create Axios instance with base configuration.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: config.baseURL,
  timeout: config.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// REQUEST INTERCEPTOR
// ============================================================================

/**
 * Request interceptor: Add auth headers and log requests in development.
 */
apiClient.interceptors.request.use(
  (requestConfig: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    // Add authentication header if API key is available
    // TODO: Replace with actual auth token when authentication is implemented
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    if (apiKey) {
      requestConfig.headers.set('X-API-Key', apiKey);
    }

    // Log requests in development mode
    if (config.debug) {
      console.warn('[API Request]', {
        method: requestConfig.method?.toUpperCase(),
        url: requestConfig.url,
        baseURL: requestConfig.baseURL,
        params: requestConfig.params,
        headers: requestConfig.headers,
      });
    }

    // Initialize retry config if not present
    if (!requestConfig._retry) {
      requestConfig._retry = {
        retries: 0,
        retryDelay: config.retryDelay,
      };
    }

    return requestConfig;
  },
  (error: AxiosError): Promise<AxiosError> => {
    // Log request errors in development
    if (config.debug) {
      console.error('[API Request Error]', error);
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// RESPONSE INTERCEPTOR
// ============================================================================

/**
 * Response interceptor: Transform responses and handle errors.
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    // Log successful responses in development mode
    if (config.debug) {
      console.warn('[API Response]', {
        status: response.status,
        statusText: response.statusText,
        url: response.config.url,
        data: response.data,
      });
    }

    // Transform response if needed (currently pass-through)
    return response;
  },
  async (error: AxiosError): Promise<never> => {
    // Log errors in development mode
    if (config.debug) {
      console.error('[API Error]', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        data: error.response?.data,
        config: {
          method: error.config?.method,
          url: error.config?.url,
        },
      });
    }

    // Handle network errors (no response from server)
    if (!error.response) {
      const networkError = transformNetworkError(error);

      // Retry network errors
      if (error.config && shouldRetry(error.config, networkError)) {
        return retryRequest(error.config);
      }

      return Promise.reject(networkError);
    }

    // Handle HTTP errors with response
    const statusCode = error.response.status;
    const errorResponse = error.response.data as ApiErrorResponse;

    // Transform error response to ApiError
    const apiError = transformErrorResponse(errorResponse, statusCode);

    // Retry retryable errors
    if (error.config && shouldRetry(error.config, apiError)) {
      return retryRequest(error.config);
    }

    return Promise.reject(apiError);
  }
);

// ============================================================================
// RETRY LOGIC
// ============================================================================

/**
 * Determines if a request should be retried.
 * 
 * @param requestConfig - Axios request configuration
 * @param error - The API error
 * @returns True if the request should be retried
 */
function shouldRetry(requestConfig: AxiosRequestConfig, error: ApiError): boolean {
  // Don't retry if retry config is not present
  if (!requestConfig._retry) {
    return false;
  }

  // Don't retry if max retries reached
  if (requestConfig._retry.retries >= config.maxRetries) {
    return false;
  }

  // Only retry if error is retryable
  return error.isRetryable;
}

/**
 * Retries a failed request with exponential backoff.
 * 
 * @param requestConfig - Axios request configuration
 * @returns Promise resolving to the response
 */
async function retryRequest(requestConfig: AxiosRequestConfig): Promise<never> {
  // Increment retry count
  requestConfig._retry!.retries += 1;

  // Calculate delay with exponential backoff
  const delay = requestConfig._retry!.retryDelay * Math.pow(2, requestConfig._retry!.retries - 1);

  if (config.debug) {
    console.warn('[API Retry]', {
      attempt: requestConfig._retry!.retries,
      maxRetries: config.maxRetries,
      delay,
      url: requestConfig.url,
    });
  }

  // Wait before retrying
  await new Promise((resolve) => setTimeout(resolve, delay));

  // Retry the request
  return apiClient.request(requestConfig);
}

// ============================================================================
// EXPORTS
// ============================================================================

export default apiClient;

/**
 * Export type-safe API client methods for convenience.
 */
export const api = {
  /**
   * Perform a GET request.
   */
  get: <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return apiClient.get<T>(url, config);
  },

  /**
   * Perform a POST request.
   */
  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return apiClient.post<T>(url, data, config);
  },

  /**
   * Perform a PUT request.
   */
  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return apiClient.put<T>(url, data, config);
  },

  /**
   * Perform a PATCH request.
   */
  patch: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return apiClient.patch<T>(url, data, config);
  },

  /**
   * Perform a DELETE request.
   */
  delete: <T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return apiClient.delete<T>(url, config);
  },
};

/**
 * Export configuration for testing and debugging.
 */
export const apiConfig = config;
