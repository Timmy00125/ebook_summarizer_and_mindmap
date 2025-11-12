# Phase 0 Research: PDF Upload with Summaries and Mindmap Generation

**Date**: November 10, 2025  
**Feature**: PDF Upload with Summaries and Mindmap Generation  
**Objective**: Resolve technical unknowns and establish best practices for implementation

---

## 1. PDF Parsing Strategy

### Decision: PyPDF2 + pdfplumber (hybrid approach)

**Rationale**:

- **PyPDF2**: Lightweight, mature, handles standard PDF text extraction and metadata
- **pdfplumber**: Better table/layout detection for complex PDFs; fallback if PyPDF2 fails
- Hybrid approach balances reliability with complexity

**Alternatives Considered**:

- ✅ **Apache PDFBox (Java)**: Industry-standard but requires JVM; adds deployment complexity
- ✅ **pypdf (pure Python)**: Sufficient for MVP; lightweight but limited layout detection
- ✅ **pdfminer.six**: Text extraction only; good for simple documents but poor table support
- **Selected**: PyPDF2 primary + pdfplumber fallback

**Implementation Notes**:

- Max PDF size: 100MB (enforced at upload time)
- Timeout: 10 seconds for parsing; fail fast if exceeded
- Extract: text content, page count, metadata (author, creation date, title)
- Error handling: Log parsing failures; queue retry; notify user if PDF corrupted

**Cost**: Minimal—both libraries are free and lightweight

---

## 2. Gemini API Integration Pattern

### Decision: Service-layer abstraction with request queuing and caching

**Rationale**:

- Decouples business logic from Gemini SDK; enables testing with mocks
- Request queuing prevents rate-limit errors; exponential backoff on failures
- Caching (LRU) reduces API calls for repeated summaries; saves cost
- Structured error handling enables retry logic and graceful degradation

**Architecture**:

```python
# backend/src/services/gemini_service.py

class GeminiService:
    def __init__(self, api_key: str, cache_max_size_mb: int = 1000):
        self.client = genai.Client(api_key=api_key)
        self.cache = LRUCache(max_size_mb)
        self.request_queue = asyncio.Queue()
        self.rate_limiter = RateLimiter(requests_per_minute=60)  # Adjust per quota

    async def generate_summary(self, text: str, max_tokens: int = 1000) -> str:
        """Generate summary with caching and rate limiting."""
        cache_key = hash(text)

        # Try cache first
        if cached := self.cache.get(cache_key):
            return cached

        # Check rate limit; queue if necessary
        await self.rate_limiter.acquire()

        try:
            response = await self.client.generate_content(
                f"Summarize: {text}",
                max_output_tokens=max_tokens,
                timeout=30  # p95 target
            )
            result = response.text
            self.cache.set(cache_key, result)
            return result
        except Exception as e:
            self._log_error(e, operation="summarize")
            # Fallback: return cached placeholder or raise
            raise GeminiAPIError(f"Summary failed: {str(e)}")

    async def generate_mindmap(self, text: str) -> dict:
        """Generate structured mindmap JSON with formatting."""
        # Similar pattern: cache, rate limit, error handling
        ...
```

**Alternatives Considered**:

- ✅ **Direct SDK calls**: Simpler initially but tight coupling; harder to test/mock
- ✅ **External queue service (RabbitMQ)**: Over-engineered for MVP; requires deployment overhead
- **Selected**: In-process queue with async/await (scalable, testable, simple)

**Cost**: Gemini API pricing scales with token usage; estimated ~$0.001-0.005 per summary (depends on document length). Implement cost tracking and budget alerts.

---

## 3. Database Schema & Persistence

### Decision: PostgreSQL with SQLAlchemy ORM + Alembic migrations

**Rationale**:

- PostgreSQL: Robust, ACID-compliant, excellent for transactional document processing
- SQLAlchemy: ORM enables testable queries; decouples from SQL dialect
- Alembic: Version-controlled migrations; enables safe schema evolution

**Core Tables**:

```sql
-- Users (for future multi-user support)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents (PDF metadata)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT,  -- S3 path or local
    file_size_bytes INT,
    page_count INT,
    extracted_text TEXT,  -- Full document text for search
    metadata JSONB,  -- PDF metadata (author, creation_date, etc.)
    upload_status ENUM('uploading', 'parsing', 'ready', 'failed'),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,  -- 30-day retention
    UNIQUE(user_id, filename)  -- Prevent duplicate uploads
);

-- Summaries
CREATE TABLE summaries (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    generation_status ENUM('queued', 'generating', 'complete', 'failed'),
    error_message TEXT,
    tokens_used INT,  -- For cost tracking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Mindmaps
CREATE TABLE mindmaps (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    mindmap_json JSONB,  -- { root: { title, children: [] } }
    generation_status ENUM('queued', 'generating', 'complete', 'failed'),
    error_message TEXT,
    tokens_used INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API logs (cost tracking + debugging)
CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id),
    operation VARCHAR(50),  -- 'summarize', 'mindmap'
    tokens_input INT,
    tokens_output INT,
    cost_usd DECIMAL(10, 6),
    latency_ms INT,
    status VARCHAR(20),  -- 'success', 'rate_limited', 'timeout', 'error'
    error_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Alternatives Considered**:

- ✅ **MongoDB**: Better for nested mindmap data but loses transaction safety for summary generation
- ✅ **Firebase**: Serverless but vendor lock-in; harder to control costs
- **Selected**: PostgreSQL + JSONB columns (best of both: relational + semi-structured)

**Retention Policy**: Documents auto-expire after 30 days; cascade delete summaries/mindmaps. Configurable via environment variable.

---

## 4. Frontend State Management & Error Handling

### Decision: Zustand for state + Axios interceptors for API errors

**Rationale**:

- **Zustand**: Lightweight, no boilerplate, perfect for document + summary/mindmap state
- **Axios interceptors**: Centralized error handling; enables auto-retry and user feedback

**Implementation**:

```typescript
// frontend/src/services/store.ts
import create from "zustand";

interface DocumentState {
  documents: Document[];
  currentDocument: Document | null;
  summary: Summary | null;
  mindmap: Mindmap | null;
  loading: boolean;
  error: string | null;

  // Actions
  setDocuments: (docs: Document[]) => void;
  setCurrentDocument: (doc: Document) => void;
  setSummary: (summary: Summary) => void;
  setMindmap: (mindmap: Mindmap) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  // ... state + actions
}));

// frontend/src/services/api.ts
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api",
  timeout: 30000,
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || "An error occurred";
    const code = error.response?.status;

    if (code === 429) {
      // Rate limited
      showNotification("Server is busy. Please retry in a moment.");
    } else if (code === 413) {
      // Payload too large
      showNotification("File too large (max 100MB)");
    } else {
      showNotification(`Error: ${message}`);
    }

    return Promise.reject(error);
  }
);
```

**Alternatives Considered**:

- ✅ **Redux**: Powerful but verbose for MVP; Zustand sufficient
- ✅ **React Context**: Simple but forces prop drilling; Zustand cleaner
- **Selected**: Zustand + Axios (minimal boilerplate, production-ready)

---

## 5. Caching Strategy for Repeated Summaries/Mindmaps

### Decision: LRU in-memory cache (1GB limit) + optional Redis for distributed caching

**Rationale**:

- **In-memory LRU**: Fast, simple, zero deployment overhead for MVP
- **Redis (optional)**: Enables shared cache across multiple backend instances; added later if scaling needed
- Cache key: `hash(document_text)` ensures identical documents share cached results

**Implementation**:

```python
# backend/src/utils/cache.py
from cachetools import LRUCache
import hashlib

class DocumentCache:
    def __init__(self, max_size_mb: int = 1000):
        self.cache = LRUCache(maxsize=max_size_mb * 1024 * 1024 / 100)  # Rough estimate
        self.stats = {"hits": 0, "misses": 0}

    def get_key(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, key: str):
        if result := self.cache.get(key):
            self.stats["hits"] += 1
            return result
        self.stats["misses"] += 1
        return None

    def set(self, key: str, value: str):
        try:
            self.cache[key] = value
        except KeyError:
            # Cache full; LRU evicts oldest
            self.cache[key] = value
```

**TTL**: No expiration for MVP (cache lives until app restart). Can add TTL-based eviction later.

---

## 6. Error Handling & Resilience

### Decision: Structured logging + retry backoff for transient failures + graceful degradation

**Rationale**:

- **Structured logging** (JSON format): Enables easy aggregation and debugging
- **Exponential backoff**: Prevents overwhelming Gemini API if rate limited
- **Graceful degradation**: If mindmap fails, still deliver summary; user informed of partial results

**Error Categories**:

| Error            | Cause                               | Retry?                    | User Message                                     |
| ---------------- | ----------------------------------- | ------------------------- | ------------------------------------------------ |
| `INVALID_PDF`    | PDF corrupted or unsupported format | No                        | "File is invalid or corrupted. Try another PDF." |
| `FILE_TOO_LARGE` | >100MB                              | No                        | "File too large (max 100MB). Try a smaller PDF." |
| `RATE_LIMITED`   | Gemini API quota exceeded           | Yes (exponential backoff) | "Server is busy. Retrying..."                    |
| `TIMEOUT`        | Gemini call exceeded 30s            | Yes (max 3x)              | "Processing took too long. Retrying..."          |
| `GEMINI_ERROR`   | API returned error                  | Yes (max 3x)              | "Service unavailable. Retrying..."               |
| `DB_ERROR`       | Database connection lost            | Yes (backoff)             | "Temporary error. Retrying..."                   |

**Implementation**:

```python
# backend/src/utils/error_handler.py
import logging
import json
from enum import Enum

class ErrorCode(Enum):
    INVALID_PDF = "INVALID_PDF"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    GEMINI_ERROR = "GEMINI_ERROR"
    DB_ERROR = "DB_ERROR"

class AppError(Exception):
    def __init__(self, code: ErrorCode, detail: str, retryable: bool = False):
        self.code = code
        self.detail = detail
        self.retryable = retryable

def log_error(error: AppError, context: dict):
    """Structured error logging."""
    logging.error(json.dumps({
        "error_code": error.code.value,
        "detail": error.detail,
        "retryable": error.retryable,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }))

async def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

---

## 7. Document Upload Flow

### Decision: Multipart form upload with streaming for large files

**Rationale**:

- **Streaming**: Prevents loading entire 100MB file into memory
- **Multipart form**: Standard HTTP; works with browser File API
- **Background processing**: Parse PDF asynchronously after upload confirmed

**Flow**:

```
1. User selects PDF → browser sends multipart POST /api/documents/upload
2. Backend receives → validates file size + MIME type
3. Save to storage (local disk or S3)
4. Queue document for async parsing (task queue or async job)
5. Return document_id + status="uploading"
6. Async task: parse PDF → extract text → store in DB → status="ready"
7. Frontend polls for status or uses WebSocket for live update
```

**Alternatives Considered**:

- ✅ **Direct S3 upload**: More complex; requires signed URLs; skip for MVP
- **Selected**: Local disk storage with optional S3 migration path

---

## 8. Performance Monitoring & Cost Tracking

### Decision: Prometheus metrics + cost logger for Gemini API

**Rationale**:

- **Prometheus**: Industry-standard for monitoring; integrates with Grafana for dashboards
- **Cost logger**: Every Gemini API call logged with token counts; enables budget tracking

**Metrics**:

- `document_upload_duration_seconds` (histogram)
- `pdf_parse_duration_seconds` (histogram)
- `gemini_summary_duration_seconds` (histogram)
- `gemini_mindmap_duration_seconds` (histogram)
- `gemini_api_tokens_used` (counter, by operation)
- `gemini_api_cost_usd` (gauge, cumulative)
- `cache_hit_ratio` (gauge)
- `error_count` (counter, by error_code)

**Implementation**:

```python
from prometheus_client import Counter, Histogram, Gauge

summary_duration = Histogram('gemini_summary_duration_seconds', 'Summary generation time', buckets=(1, 2, 5, 10))
tokens_counter = Counter('gemini_api_tokens_used', 'Tokens consumed', ['operation'])
cost_gauge = Gauge('gemini_api_cost_usd', 'Cumulative API cost')
```

---

## 9. API Contract: Gemini Request/Response Format

### Decision: Prompt templates with structured output (JSON)

**Rationale**:

- **Structured prompts**: Ensures consistent, repeatable Gemini API results
- **JSON output**: Enables parsing and validation; structured mindmaps

**Summary Prompt Template**:

```
Summarize the following document in clear, concise bullet points. Focus on key concepts, findings, and conclusions. Output 5-10 bullets.

Document:
{DOCUMENT_TEXT}

Summary:
```

**Mindmap Prompt Template**:

```
Convert the following document into a hierarchical mindmap structure. Return valid JSON with format:
{
  "title": "Document title",
  "children": [
    {
      "title": "Main concept",
      "children": [
        {"title": "Subtopic", "children": []}
      ]
    }
  ]
}

Document:
{DOCUMENT_TEXT}

Mindmap JSON:
```

**Error Handling**: If Gemini returns invalid JSON, log error and retry with simpler prompt.

---

## 10. Testing Strategy

### Decision: Unit tests (70%) + Integration tests (15%) + Contract tests (10%) + E2E (5%)

**Coverage Target**: ≥80% for production code (enforced by CI)

**Test Types**:

1. **Unit Tests** (70%):

   - PDF parsing (valid/invalid files, edge cases)
   - Summary/mindmap generation (prompt validation, response parsing)
   - Error handling (retry logic, timeouts)
   - Caching (LRU eviction, hit/miss)

2. **Integration Tests** (15%):

   - Full upload → parse → summary flow
   - Full upload → parse → mindmap flow
   - Database CRUD operations
   - Gemini API rate limiting + retry

3. **Contract Tests** (10%):

   - Mock Gemini responses (summarize, generate mindmap)
   - Mock database operations
   - Verify API contracts (request/response shapes)

4. **E2E Tests** (5%):
   - Browser-based upload flow (Playwright)
   - View summary/mindmap in UI
   - Download/export functionality

**Mock Strategy**:

```python
# tests/contract/test_gemini_contract.py
@pytest.fixture
def mock_gemini_client(monkeypatch):
    def mock_generate_content(prompt: str, **kwargs):
        return MockResponse(text="Mock summary content")

    monkeypatch.setattr(genai.Client, "generate_content", mock_generate_content)

def test_summary_generation_with_mock(mock_gemini_client):
    service = GeminiService(api_key="test")
    result = service.generate_summary("test document")
    assert result == "Mock summary content"
```

---

## Summary of Decisions

| Area               | Decision                                   | Rationale                                 |
| ------------------ | ------------------------------------------ | ----------------------------------------- |
| PDF Parsing        | PyPDF2 + pdfplumber                        | Lightweight, hybrid reliability           |
| Gemini Integration | Service abstraction + queuing + caching    | Decoupled, resilient, cost-optimized      |
| Database           | PostgreSQL + SQLAlchemy + Alembic          | ACID, ORM, versioned migrations           |
| State Management   | Zustand + Axios interceptors               | Minimal boilerplate, production-ready     |
| Caching            | LRU in-memory (1GB)                        | Fast, zero overhead; Redis optional later |
| Error Handling     | Structured logging + retry backoff         | Observable, resilient, user-friendly      |
| Upload             | Multipart form + streaming + async parse   | Efficient, non-blocking                   |
| Monitoring         | Prometheus metrics + cost logging          | Observability + budget control            |
| API Format         | Structured prompts + JSON responses        | Consistent, parseable                     |
| Testing            | 80% coverage (unit-heavy) + contract mocks | TDD-compliant, maintainable               |

**All decisions align with Constitution principles** (TDD, Clarity, Performance, Error Handling, API Discipline).

**Next Phase**: Phase 1 will generate `data-model.md`, API contracts, and `quickstart.md`.
