# Zustand Document Store

This directory contains the Zustand state management store for the eBook Summarizer and Mindmap application.

## Files

- **`store.ts`**: Main Zustand store with TypeScript types and actions
- **`store.examples.tsx`**: Example React components demonstrating store usage

## Features

### TypeScript Types

The store includes complete TypeScript types that match the backend models:

- `Document`: PDF document metadata and processing status
- `Summary`: Generated document summaries
- `Mindmap`: Hierarchical mindmap structure
- `UploadStatus`: Document upload states (uploading, parsing, ready, failed)
- `GenerationStatus`: Summary/mindmap generation states (queued, generating, complete, failed)

### State Management

The `DocumentState` interface includes:

- **Data**:
  - `documents`: Array of all documents
  - `currentDocument`: Currently selected document (or null)

- **Loading States**:
  - `loading.documents`: Loading documents list
  - `loading.upload`: Uploading a document
  - `loading.summary`: Generating summary
  - `loading.mindmap`: Generating mindmap

- **Error States**:
  - `errors.documents`: Error fetching documents
  - `errors.upload`: Error uploading document
  - `errors.summary`: Error generating summary
  - `errors.mindmap`: Error generating mindmap

### Actions

#### Document Actions
- `setDocuments(documents)`: Set the entire documents array
- `setCurrentDocument(document)`: Set the currently selected document
- `addDocument(document)`: Add a new document to the list
- `updateDocument(id, updates)`: Update a document by ID (also updates currentDocument if it's the same)
- `deleteDocument(id)`: Delete a document by ID (also clears currentDocument if it's the same)

#### Loading Actions
- `setLoading(key, value)`: Set a loading state (e.g., `setLoading('documents', true)`)

#### Error Actions
- `setError(key, error)`: Set an error message (or undefined to clear)
- `clearErrors()`: Clear all error messages

#### Utility Actions
- `reset()`: Reset store to initial state

### LocalStorage Persistence

The store uses Zustand's `persist` middleware to save state to localStorage:

- **Persisted**: `documents`, `currentDocument`
- **Not Persisted**: `loading`, `errors` (these are transient states)
- **Storage Key**: `document-storage`

This provides better UX by maintaining state across page refreshes.

## Usage Examples

### Basic Hook Usage

```tsx
import { useDocumentStore } from '@/lib/services/store';

function MyComponent() {
  // Read state
  const documents = useDocumentStore((state) => state.documents);
  const loading = useDocumentStore((state) => state.loading.documents);
  
  // Get actions
  const setDocuments = useDocumentStore((state) => state.setDocuments);
  const addDocument = useDocumentStore((state) => state.addDocument);
  
  // Use in component logic
  // ...
}
```

### Fetching Documents

```tsx
const setDocuments = useDocumentStore((state) => state.setDocuments);
const setLoading = useDocumentStore((state) => state.setLoading);
const setError = useDocumentStore((state) => state.setError);

async function fetchDocuments() {
  try {
    setLoading('documents', true);
    setError('documents', undefined);
    
    const response = await fetch('/api/documents');
    if (!response.ok) throw new Error('Failed to fetch');
    
    const documents = await response.json();
    setDocuments(documents);
  } catch (err) {
    setError('documents', err instanceof Error ? err.message : 'Unknown error');
  } finally {
    setLoading('documents', false);
  }
}
```

### Uploading a Document

```tsx
const addDocument = useDocumentStore((state) => state.addDocument);
const setLoading = useDocumentStore((state) => state.setLoading);
const setError = useDocumentStore((state) => state.setError);

async function uploadDocument(file: File) {
  try {
    setLoading('upload', true);
    setError('upload', undefined);
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Failed to upload');
    
    const document = await response.json();
    addDocument(document);
  } catch (err) {
    setError('upload', err instanceof Error ? err.message : 'Unknown error');
  } finally {
    setLoading('upload', false);
  }
}
```

### Updating Document Status

```tsx
const updateDocument = useDocumentStore((state) => state.updateDocument);

// Update upload status
updateDocument(documentId, { upload_status: 'parsing' });

// Update with summary
updateDocument(documentId, {
  summary: {
    id: 1,
    document_id: documentId,
    summary_text: 'Generated summary...',
    generation_status: 'complete',
    tokens_input: 1000,
    tokens_output: 500,
    latency_ms: 2000,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
});
```

### Working with Current Document

```tsx
const currentDocument = useDocumentStore((state) => state.currentDocument);
const setCurrentDocument = useDocumentStore((state) => state.setCurrentDocument);

// Select a document
function selectDocument(doc: Document) {
  setCurrentDocument(doc);
}

// Clear selection
function closeDocument() {
  setCurrentDocument(null);
}

// Render current document
if (currentDocument) {
  return (
    <div>
      <h2>{currentDocument.filename}</h2>
      <p>Status: {currentDocument.upload_status}</p>
    </div>
  );
}
```

### Deleting a Document

```tsx
const deleteDocument = useDocumentStore((state) => state.deleteDocument);

async function handleDelete(documentId: number) {
  try {
    const response = await fetch(`/api/documents/${documentId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) throw new Error('Failed to delete');
    
    // Remove from store
    deleteDocument(documentId);
  } catch (err) {
    console.error('Delete failed:', err);
  }
}
```

## Best Practices

1. **Use Selectors**: Only subscribe to the state you need
   ```tsx
   // Good - only re-renders when documents change
   const documents = useDocumentStore((state) => state.documents);
   
   // Bad - re-renders on any state change
   const store = useDocumentStore();
   ```

2. **Clear Errors**: Clear errors before new operations
   ```tsx
   setError('documents', undefined);
   // or
   clearErrors();
   ```

3. **Loading States**: Always set loading states for async operations
   ```tsx
   setLoading('documents', true);
   try {
     // async operation
   } finally {
     setLoading('documents', false);
   }
   ```

4. **Update Current Document**: When updating a document, the store automatically updates `currentDocument` if it's the same document

5. **Reset on Logout**: Call `reset()` when user logs out to clear all state

## Architecture Notes

- The store follows the backend model structure for consistency
- All timestamps are ISO 8601 strings (e.g., "2024-01-01T00:00:00Z")
- Upload status values match backend enum: "uploading", "parsing", "ready", "failed"
- Generation status values match backend enum: "queued", "generating", "complete", "failed"
- The store is a single source of truth for document state in the frontend
