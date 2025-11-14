/**
 * Zustand State Management Store
 * Manages application state for documents, summaries, and mindmaps
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Document upload status
 * Matches backend enum: uploading, parsing, ready, failed
 */
export type UploadStatus = 'uploading' | 'parsing' | 'ready' | 'failed';

/**
 * Generation status for summaries and mindmaps
 * Matches backend enum: queued, generating, complete, failed
 */
export type GenerationStatus = 'queued' | 'generating' | 'complete' | 'failed';

/**
 * Summary entity - matches backend Summary model
 */
export interface Summary {
  id: number;
  document_id: number;
  summary_text: string;
  generation_status: GenerationStatus;
  error_message?: string;
  tokens_input: number;
  tokens_output: number;
  latency_ms: number;
  created_at: string;
  updated_at: string;
}

/**
 * Mindmap node structure
 */
export interface MindmapNode {
  title: string;
  children?: MindmapNode[];
}

/**
 * Mindmap entity - matches backend Mindmap model
 */
export interface Mindmap {
  id: number;
  document_id: number;
  mindmap_json: MindmapNode;
  generation_status: GenerationStatus;
  error_message?: string;
  tokens_input: number;
  tokens_output: number;
  latency_ms: number;
  created_at: string;
  updated_at: string;
}

/**
 * PDF metadata extracted from document
 */
export interface PDFMetadata {
  author?: string;
  creation_date?: string;
  title?: string;
  subject?: string;
}

/**
 * Document entity - matches backend Document model
 */
export interface Document {
  id: number;
  user_id: number;
  filename: string;
  file_path: string;
  file_size_bytes: number;
  file_hash: string;
  page_count?: number;
  extracted_text?: string;
  pdf_metadata?: PDFMetadata;
  upload_status: UploadStatus;
  error_message?: string;
  created_at: string;
  updated_at: string;
  expires_at: string;
  summary?: Summary;
  mindmap?: Mindmap;
}

/**
 * Loading states for different operations
 */
export interface LoadingStates {
  documents: boolean;
  upload: boolean;
  summary: boolean;
  mindmap: boolean;
}

/**
 * Error states for different operations
 */
export interface ErrorStates {
  documents?: string;
  upload?: string;
  summary?: string;
  mindmap?: string;
}

// ============================================================================
// Store State Interface
// ============================================================================

/**
 * Main document state interface
 */
export interface DocumentState {
  // Data
  documents: Document[];
  currentDocument: Document | null;

  // Loading states
  loading: LoadingStates;

  // Error states
  errors: ErrorStates;

  // Actions
  setDocuments: (documents: Document[]) => void;
  setCurrentDocument: (document: Document | null) => void;
  addDocument: (document: Document) => void;
  updateDocument: (id: number, updates: Partial<Document>) => void;
  deleteDocument: (id: number) => void;

  // Loading actions
  setLoading: (key: keyof LoadingStates, value: boolean) => void;

  // Error actions
  setError: (key: keyof ErrorStates, error: string | undefined) => void;
  clearErrors: () => void;

  // Reset action
  reset: () => void;
}

// ============================================================================
// Initial State
// ============================================================================

const initialState = {
  documents: [],
  currentDocument: null,
  loading: {
    documents: false,
    upload: false,
    summary: false,
    mindmap: false,
  },
  errors: {},
};

// ============================================================================
// Zustand Store
// ============================================================================

/**
 * Main Zustand store with localStorage persistence
 * Persists documents and currentDocument to localStorage for better UX
 */
export const useDocumentStore = create<DocumentState>()(
  persist(
    (set) => ({
      ...initialState,

      // ======================================================================
      // Document Actions
      // ======================================================================

      setDocuments: (documents: Document[]) =>
        set({ documents }),

      setCurrentDocument: (document: Document | null) =>
        set({ currentDocument: document }),

      addDocument: (document: Document) =>
        set((state) => ({
          documents: [...state.documents, document],
        })),

      updateDocument: (id: number, updates: Partial<Document>) =>
        set((state) => {
          const documents = state.documents.map((doc) =>
            doc.id === id ? { ...doc, ...updates } : doc
          );

          // Update currentDocument if it's the one being updated
          const currentDocument =
            state.currentDocument?.id === id
              ? { ...state.currentDocument, ...updates }
              : state.currentDocument;

          return { documents, currentDocument };
        }),

      deleteDocument: (id: number) =>
        set((state) => ({
          documents: state.documents.filter((doc) => doc.id !== id),
          currentDocument:
            state.currentDocument?.id === id ? null : state.currentDocument,
        })),

      // ======================================================================
      // Loading Actions
      // ======================================================================

      setLoading: (key: keyof LoadingStates, value: boolean) =>
        set((state) => ({
          loading: {
            ...state.loading,
            [key]: value,
          },
        })),

      // ======================================================================
      // Error Actions
      // ======================================================================

      setError: (key: keyof ErrorStates, error: string | undefined) =>
        set((state) => ({
          errors: {
            ...state.errors,
            [key]: error,
          },
        })),

      clearErrors: () =>
        set({ errors: {} }),

      // ======================================================================
      // Reset Action
      // ======================================================================

      reset: () =>
        set(initialState),
    }),
    {
      name: 'document-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      // Only persist documents and currentDocument, not loading/error states
      partialize: (state) => ({
        documents: state.documents,
        currentDocument: state.currentDocument,
      }),
    }
  )
);
