/**
 * Example usage of the Zustand Document Store
 * This file demonstrates how to use the store in React components
 */

'use client';

import { useDocumentStore, Document } from './store';

/**
 * Example Component - Document List
 * Shows how to read documents from the store
 */
export function DocumentList() {
  const documents = useDocumentStore((state) => state.documents);
  const loading = useDocumentStore((state) => state.loading.documents);
  const error = useDocumentStore((state) => state.errors.documents);

  if (loading) return <div>Loading documents...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Documents</h2>
      {documents.length === 0 ? (
        <p>No documents found</p>
      ) : (
        <ul>
          {documents.map((doc) => (
            <li key={doc.id}>
              {doc.filename} - {doc.upload_status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/**
 * Example Component - Document Actions
 * Shows how to use store actions
 */
export function DocumentActions() {
  const setDocuments = useDocumentStore((state) => state.setDocuments);
  const addDocument = useDocumentStore((state) => state.addDocument);
  const setLoading = useDocumentStore((state) => state.setLoading);
  const setError = useDocumentStore((state) => state.setError);

  const handleFetchDocuments = async () => {
    try {
      setLoading('documents', true);
      setError('documents', undefined);

      // Example API call
      const response = await fetch('/api/documents');
      if (!response.ok) throw new Error('Failed to fetch documents');

      const documents = await response.json();
      setDocuments(documents);
    } catch (err) {
      setError('documents', err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading('documents', false);
    }
  };

  const handleUploadDocument = async (file: File) => {
    try {
      setLoading('upload', true);
      setError('upload', undefined);

      // Example upload API call
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to upload document');

      const newDocument: Document = await response.json();
      addDocument(newDocument);
    } catch (err) {
      setError('upload', err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading('upload', false);
    }
  };

  return (
    <div>
      <button onClick={handleFetchDocuments}>Fetch Documents</button>
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUploadDocument(file);
        }}
      />
    </div>
  );
}

/**
 * Example Component - Current Document
 * Shows how to work with the current document
 */
export function CurrentDocumentViewer() {
  const currentDocument = useDocumentStore((state) => state.currentDocument);
  const setCurrentDocument = useDocumentStore((state) => state.setCurrentDocument);
  const updateDocument = useDocumentStore((state) => state.updateDocument);

  if (!currentDocument) {
    return <div>No document selected</div>;
  }

  const handleGenerateSummary = async () => {
    try {
      // Update document status
      updateDocument(currentDocument.id, { upload_status: 'parsing' });

      // Example API call
      const response = await fetch(`/api/documents/${currentDocument.id}/summary`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to generate summary');

      const updatedDocument = await response.json();
      updateDocument(currentDocument.id, updatedDocument);
    } catch (err) {
      console.error('Failed to generate summary:', err);
    }
  };

  return (
    <div>
      <h2>Current Document</h2>
      <p>Filename: {currentDocument.filename}</p>
      <p>Status: {currentDocument.upload_status}</p>
      <p>Pages: {currentDocument.page_count || 'N/A'}</p>

      {currentDocument.summary && (
        <div>
          <h3>Summary</h3>
          <p>{currentDocument.summary.summary_text}</p>
        </div>
      )}

      <button onClick={handleGenerateSummary}>Generate Summary</button>
      <button onClick={() => setCurrentDocument(null)}>Close</button>
    </div>
  );
}
