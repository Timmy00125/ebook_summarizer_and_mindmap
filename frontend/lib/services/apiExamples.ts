/**
 * Example usage of the API client.
 * 
 * This file demonstrates how to use the API client for common operations.
 * Import this in your components to interact with the backend API.
 */

import { api } from '@/lib/services';
import {
  ApiError,
  DocumentDetail,
  DocumentResponse,
  HealthCheckResponse,
  PaginatedResponse,
  SummaryResponse,
} from '@/lib/types';

/**
 * Example: Health check
 */
export async function checkHealth(): Promise<HealthCheckResponse> {
  try {
    const response = await api.get<HealthCheckResponse>('/health');
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Health check failed:', error.message);
      throw error;
    }
    throw error;
  }
}

/**
 * Example: List documents with pagination
 */
export async function listDocuments(
  skip: number = 0,
  limit: number = 20
): Promise<PaginatedResponse<DocumentResponse>> {
  try {
    const response = await api.get<PaginatedResponse<DocumentResponse>>('/documents', {
      params: { skip, limit },
    });
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Failed to list documents:', error.message);
      throw error;
    }
    throw error;
  }
}

/**
 * Example: Upload a PDF document
 */
export async function uploadDocument(file: File): Promise<DocumentResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<DocumentResponse>('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Failed to upload document:', error.message);
      throw error;
    }
    throw error;
  }
}

/**
 * Example: Get document details
 */
export async function getDocument(documentId: number): Promise<DocumentDetail> {
  try {
    const response = await api.get<DocumentDetail>(`/documents/${documentId}`);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Failed to get document:', error.message);
      throw error;
    }
    throw error;
  }
}

/**
 * Example: Generate summary for a document
 */
export async function generateSummary(documentId: number): Promise<SummaryResponse> {
  try {
    const response = await api.post<SummaryResponse>(`/documents/${documentId}/summary`);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Failed to generate summary:', error.message);
      throw error;
    }
    throw error;
  }
}

/**
 * Example: Delete a document
 */
export async function deleteDocument(documentId: number): Promise<void> {
  try {
    await api.delete(`/documents/${documentId}`);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Failed to delete document:', error.message);
      throw error;
    }
    throw error;
  }
}
