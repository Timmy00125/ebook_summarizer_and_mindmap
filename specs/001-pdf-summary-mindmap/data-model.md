# Phase 1 Data Model: PDF Upload with Summaries and Mindmap Generation

**Date**: November 10, 2025  
**Feature**: PDF Upload with Summaries and Mindmap Generation  
**Phase**: 1 (Design)

---

## Data Entities

### 1. User

**Purpose**: Account management for multi-user support (MVP: single user, but extensible)

| Field        | Type        | Constraints        | Notes                    |
| ------------ | ----------- | ------------------ | ------------------------ |
| `id`         | Integer     | PK, AUTO_INCREMENT | Unique identifier        |
| `email`      | String(255) | UNIQUE, NOT NULL   | Email for authentication |
| `name`       | String(255) | NOT NULL           | User display name        |
| `created_at` | Timestamp   | DEFAULT NOW()      | Account creation time    |
| `updated_at` | Timestamp   | DEFAULT NOW()      | Last updated time        |
| `deleted_at` | Timestamp   | NULLABLE           | Soft delete flag         |

**Indexes**:

- UNIQUE INDEX on `email` (fast auth lookup)
- INDEX on `created_at` (user list pagination)

**Validation Rules**:

- Email must be valid (RFC 5322)
- Name length: 1-255 characters

---

### 2. Document

**Purpose**: PDF document metadata and processing status

| Field             | Type        | Constraints             | Notes                                                   |
| ----------------- | ----------- | ----------------------- | ------------------------------------------------------- |
| `id`              | Integer     | PK, AUTO_INCREMENT      | Unique identifier                                       |
| `user_id`         | Integer     | FK → User(id), NOT NULL | Owner of document                                       |
| `filename`        | String(255) | NOT NULL                | Original filename (e.g., "research.pdf")                |
| `file_path`       | Text        | NOT NULL                | Full path to stored file (local or S3)                  |
| `file_size_bytes` | Integer     | NOT NULL                | Size for quota enforcement                              |
| `file_hash`       | String(64)  | UNIQUE, NOT NULL        | SHA-256 hash for dedup                                  |
| `page_count`      | Integer     | NULLABLE                | Number of pages (extracted during parse)                |
| `extracted_text`  | Text        | NULLABLE                | Full document text (for full-text search)               |
| `metadata`        | JSONB       | NULLABLE                | PDF metadata: `{author, creation_date, title, subject}` |
| `upload_status`   | ENUM        | DEFAULT 'uploading'     | States: uploading, parsing, ready, failed               |
| `error_message`   | Text        | NULLABLE                | Human-readable error if upload/parse fails              |
| `created_at`      | Timestamp   | DEFAULT NOW()           | Upload timestamp                                        |
| `updated_at`      | Timestamp   | DEFAULT NOW()           | Last status update                                      |
| `expires_at`      | Timestamp   | NOT NULL                | Auto-delete date (30 days from upload)                  |

**Indexes**:

- FK INDEX on `user_id` (fast query by user)
- UNIQUE INDEX on `(user_id, file_hash)` (prevent duplicate uploads by same user)
- INDEX on `created_at` (document list pagination)
- INDEX on `upload_status` (find documents needing processing)
- INDEX on `expires_at` (cleanup queries)

**Validation Rules**:

- `filename` must be non-empty
- `file_size_bytes` must be ≤100 MB (10^8 bytes)
- `file_hash` must be valid SHA-256 (64 hex chars)
- `upload_status` transition rules:
  - uploading → parsing → ready (success path)
  - uploading/parsing → failed (error path)
  - ready is terminal for parsing; new summaries/mindmaps don't change status

**State Transitions**:

```
uploading (user uploads file)
  ├→ parsing (backend starts parsing)
  │   ├→ ready (parse succeeded; text extracted)
  │   └→ failed (parse failed; error logged)
  └→ failed (upload failed; file not saved)
```

**Retention Policy**:

- Documents expire 30 days after upload
- Cleanup job daily: DELETE WHERE expires_at < NOW()
- Cascade delete: all summaries/mindmaps for document also deleted

---

### 3. Summary

**Purpose**: Generated document summary (text)

| Field               | Type      | Constraints                         | Notes                                               |
| ------------------- | --------- | ----------------------------------- | --------------------------------------------------- |
| `id`                | Integer   | PK, AUTO_INCREMENT                  | Unique identifier                                   |
| `document_id`       | Integer   | FK → Document(id), NOT NULL, UNIQUE | 1:1 relationship (one summary per document MVP)     |
| `summary_text`      | Text      | NOT NULL                            | Summary content (formatted with bullets/paragraphs) |
| `generation_status` | ENUM      | DEFAULT 'queued'                    | States: queued, generating, complete, failed        |
| `error_message`     | Text      | NULLABLE                            | Error detail if generation fails                    |
| `tokens_input`      | Integer   | NOT NULL                            | Gemini API input tokens (for cost tracking)         |
| `tokens_output`     | Integer   | NOT NULL                            | Gemini API output tokens                            |
| `latency_ms`        | Integer   | NOT NULL                            | API call latency                                    |
| `created_at`        | Timestamp | DEFAULT NOW()                       | Generation timestamp                                |
| `updated_at`        | Timestamp | DEFAULT NOW()                       | Status update timestamp                             |

**Indexes**:

- FK INDEX on `document_id`
- INDEX on `generation_status` (find incomplete summaries for retry)
- INDEX on `created_at` (log queries)

**Validation Rules**:

- `summary_text` must be non-empty after generation
- `tokens_input` and `tokens_output` must be ≥0
- `latency_ms` must be ≥0 and <30000 (30s timeout)
- `generation_status` transition rules:
  - queued → generating → complete (success path)
  - queued/generating → failed (error path)
  - complete is terminal; retry creates new Summary record

**State Transitions**:

```
queued (user requests summary)
  ├→ generating (Gemini API call in progress)
  │   ├→ complete (success; text stored)
  │   └→ failed (API error; max 3 retries per Constitution)
  └→ failed (immediate validation error)
```

**Cost Tracking**:

- Each Summary logs tokens consumed
- Daily cost report: SUM(tokens_output) \* $rate_per_output_token

---

### 4. Mindmap

**Purpose**: Generated hierarchical mindmap (JSON)

| Field               | Type      | Constraints                         | Notes                                            |
| ------------------- | --------- | ----------------------------------- | ------------------------------------------------ |
| `id`                | Integer   | PK, AUTO_INCREMENT                  | Unique identifier                                |
| `document_id`       | Integer   | FK → Document(id), NOT NULL, UNIQUE | 1:1 relationship (MVP)                           |
| `mindmap_json`      | JSONB     | NOT NULL                            | Structured hierarchy: `{title, children: [...]}` |
| `generation_status` | ENUM      | DEFAULT 'queued'                    | States: queued, generating, complete, failed     |
| `error_message`     | Text      | NULLABLE                            | Error detail if generation fails                 |
| `tokens_input`      | Integer   | NOT NULL                            | Gemini API input tokens                          |
| `tokens_output`     | Integer   | NOT NULL                            | Gemini API output tokens                         |
| `latency_ms`        | Integer   | NOT NULL                            | API call latency                                 |
| `created_at`        | Timestamp | DEFAULT NOW()                       | Generation timestamp                             |
| `updated_at`        | Timestamp | DEFAULT NOW()                       | Status update timestamp                          |

**Indexes**:

- FK INDEX on `document_id`
- INDEX on `generation_status` (find incomplete mindmaps for retry)

**JSON Schema**:

```json
{
  "title": "Document Title",
  "children": [
    {
      "title": "Main Concept 1",
      "children": [
        {
          "title": "Subtopic 1.1",
          "children": []
        },
        {
          "title": "Subtopic 1.2",
          "children": []
        }
      ]
    },
    {
      "title": "Main Concept 2",
      "children": [...]
    }
  ]
}
```

**Validation Rules**:

- `mindmap_json` must be valid JSON
- Root object must have `title` (string) and `children` (array)
- Each child must follow same structure recursively
- Max depth: 10 levels (prevent malformed output from Gemini)
- Max nodes: 500 (prevent memory issues in frontend)

**State Transitions**: Same as Summary

**Cost Tracking**: Same as Summary

---

### 5. APILog

**Purpose**: Audit trail for all Gemini API calls (debugging + cost tracking)

| Field           | Type           | Constraints                 | Notes                                              |
| --------------- | -------------- | --------------------------- | -------------------------------------------------- |
| `id`            | Integer        | PK, AUTO_INCREMENT          | Unique identifier                                  |
| `document_id`   | Integer        | FK → Document(id), NULLABLE | Document being processed (NULL for metadata calls) |
| `operation`     | String(50)     | NOT NULL                    | "summarize" or "mindmap"                           |
| `tokens_input`  | Integer        | NOT NULL                    | Input tokens                                       |
| `tokens_output` | Integer        | NOT NULL                    | Output tokens                                      |
| `cost_usd`      | Decimal(10, 6) | NOT NULL                    | Calculated cost (tokens \* rate)                   |
| `latency_ms`    | Integer        | NOT NULL                    | API latency                                        |
| `status`        | String(20)     | NOT NULL                    | "success", "rate_limited", "timeout", "error"      |
| `error_code`    | String(50)     | NULLABLE                    | "RATE_LIMIT", "TIMEOUT", "AUTH_ERROR", etc.        |
| `created_at`    | Timestamp      | DEFAULT NOW()               | Request timestamp                                  |

**Indexes**:

- INDEX on `created_at` (cost reports)
- INDEX on `operation` (operation-specific reports)
- INDEX on `status` (error analysis)

**Validation Rules**:

- `operation` must be in ("summarize", "mindmap")
- `status` must be in ("success", "rate_limited", "timeout", "error")
- `cost_usd` must be ≥0
- `latency_ms` must be ≥0

**Reporting**:

- Daily cost: SUM(cost_usd) WHERE created_at >= TODAY()
- Error rate: COUNT(_) WHERE status != 'success' / COUNT(_)
- P95 latency: PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)

---

### 6. DocumentCache (Runtime, not persisted)

**Purpose**: In-memory LRU cache for summaries/mindmaps (Python object, not DB table)

```python
class DocumentCache:
    def __init__(self, max_size_mb: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size_mb
        self.current_size = 0

    class CacheEntry:
        key: str  # SHA-256(document_text)
        summary: Optional[str]
        mindmap: Optional[dict]
        created_at: datetime
        accessed_at: datetime
```

**Eviction Policy**: LRU (least recently used)
**TTL**: None for MVP (persist until app restart)
**Hit Rate Target**: >70% for repeated summaries

---

## Relationships & Constraints

### Entity Relationship Diagram (ERD)

```
User (1) ──── (N) Document
             │
             ├─── (1) Summary
             └─── (1) Mindmap

Document → APILog (1:N) [audit trail]
```

### Foreign Key Constraints

| Constraint                        | Details                                               |
| --------------------------------- | ----------------------------------------------------- |
| Document.user_id → User.id        | ON DELETE CASCADE (when user deleted, docs deleted)   |
| Summary.document_id → Document.id | ON DELETE CASCADE (when doc deleted, summary deleted) |
| Mindmap.document_id → Document.id | ON DELETE CASCADE                                     |
| APILog.document_id → Document.id  | ON DELETE SET NULL (preserve audit trail)             |

### Unique Constraints

| Constraint                   | Reason                                                      |
| ---------------------------- | ----------------------------------------------------------- |
| User.email                   | Prevent duplicate accounts                                  |
| Document(user_id, file_hash) | Prevent duplicate PDF uploads by same user                  |
| Summary.document_id          | One summary per document (MVP; extend later for versioning) |
| Mindmap.document_id          | One mindmap per document                                    |

---

## Validation Rules & Business Logic

### Document Upload Validation

```python
def validate_document_upload(file: UploadFile) -> None:
    # File size
    if file.size > 100_000_000:  # 100 MB
        raise ValidationError("INVALID_FILE_SIZE", "File too large (max 100MB)")

    # MIME type
    if file.content_type != "application/pdf":
        raise ValidationError("INVALID_MIME_TYPE", "Only PDF files allowed")

    # Filename
    if not file.filename or len(file.filename) > 255:
        raise ValidationError("INVALID_FILENAME", "Filename too long")

    # Duplicate check
    existing = db.query(Document).filter(
        Document.user_id == user_id,
        Document.file_hash == sha256(file.content)
    ).first()
    if existing:
        raise ValidationError("DUPLICATE_FILE", "This PDF is already uploaded")
```

### Summary Generation Validation

```python
def validate_summary_generation(document: Document) -> None:
    # Document must be parsed
    if document.upload_status != "ready":
        raise ValidationError("DOCUMENT_NOT_READY",
                            f"Document status: {document.upload_status}")

    # Document text extracted
    if not document.extracted_text:
        raise ValidationError("NO_TEXT", "Could not extract text from PDF")

    # Existing summary
    existing_summary = db.query(Summary).filter(
        Summary.document_id == document.id,
        Summary.generation_status == "complete"
    ).first()
    if existing_summary:
        return existing_summary  # Return cached summary instead of re-generating
```

### Mindmap JSON Validation

```python
def validate_mindmap_json(json_obj: dict) -> None:
    def validate_node(node: dict, depth: int = 0) -> None:
        if depth > 10:
            raise ValidationError("MAX_DEPTH_EXCEEDED", "Mindmap too deep")

        if "title" not in node or not isinstance(node["title"], str):
            raise ValidationError("MISSING_TITLE", "All nodes must have title")

        if "children" not in node or not isinstance(node["children"], list):
            raise ValidationError("MISSING_CHILDREN", "All nodes must have children array")

        if len(node["children"]) > 100:
            raise ValidationError("TOO_MANY_CHILDREN", "Max 100 children per node")

        for child in node["children"]:
            validate_node(child, depth + 1)

    validate_node(json_obj)
```

---

## Data Flow

### Upload → Parse → Summary Flow

```
1. User uploads PDF
   └─→ Document.upload_status = "uploading"
       └─→ Save file to storage
           └─→ Document.upload_status = "parsing"
               └─→ Async task: extract text + metadata
                   ├─→ Success: Document.upload_status = "ready"
                   │           Document.extracted_text = "..."
                   └─→ Error:  Document.upload_status = "failed"
                               Document.error_message = "..."

2. User requests summary
   └─→ Query Document.extracted_text
       └─→ Check cache (SHA-256(text))
           ├─→ Cache hit: return Summary from cache
           └─→ Cache miss:
               └─→ Summary.generation_status = "queued"
                   └─→ Async task: call Gemini API
                       ├─→ Success: Summary.generation_status = "complete"
                       │             Summary.summary_text = "..."
                       │             Cache result
                       └─→ Error (retryable): retry with backoff
                       └─→ Error (non-retryable): Summary.generation_status = "failed"
                                                   Summary.error_message = "..."
```

### Parallel Mindmap Generation

```
Same as above, but generates Mindmap record with:
- Mindmap.mindmap_json = { structured hierarchy }
- Mindmap.generation_status = "complete"
```

---

## Migration Strategy

### Initial Schema (Phase 1)

- Create `users` table (extensible for multi-user)
- Create `documents`, `summaries`, `mindmaps`, `api_logs` tables
- All tables versioned via Alembic migrations

### Future Enhancements (Phase 2+)

- Add `documents_versions` table for version history
- Add `summaries_versions` table for A/B testing different summaries
- Add `user_preferences` table for customization
- Add `shared_documents` table for collaboration

---

## Summary

**Total Entities**: 6 (User, Document, Summary, Mindmap, APILog, DocumentCache)
**Total Indexed Fields**: ~25 (for query performance)
**Cascade Behavior**: Delete user → delete all documents → delete all summaries/mindmaps → preserve APILog (audit)
**Constraints Enforced**: Not null, unique, FK relationships, enum validation
**Performance Targets**: <100ms for typical queries (user documents, summary lookups)

**All entities validated against Constitution principles**:

- ✅ **TDD**: Schema validated by contract tests (migration tests)
- ✅ **Clarity**: Entity names self-documenting; fields minimize ambiguity
- ✅ **Performance**: Strategic indexing for common queries; JSONB for flexible metadata
- ✅ **Error Handling**: status fields track processing state; error_message for transparency
- ✅ **API Discipline**: APILog provides audit trail for all external API calls

**Next**: Generate API contracts and quickstart guide.
