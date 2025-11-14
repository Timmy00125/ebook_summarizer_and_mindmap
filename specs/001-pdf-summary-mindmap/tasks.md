# Tasks: PDF Upload with Summaries and Mindmap Generation

**Input**: Design documents from `/specs/001-pdf-summary-mindmap/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Test tasks are included per Constitution requirements (80%+ coverage enforced by CI)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a full-stack web application with:

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/app/`, `frontend/lib/`, `frontend/components/`, `frontend/tests/` (Next.js App Router)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both backend and frontend

- [x] T001 Create backend project structure per plan.md: src/{models,services,api,utils,middleware}, tests/{unit,integration,contract,e2e}
- [x] T002 Create frontend project structure for Next.js App Router: lib/{services,types,utils}, components/, tests/{unit,e2e} (app/ directory already exists)
- [x] T003 [P] Initialize Python backend with FastAPI dependencies in backend/requirements.txt (FastAPI 0.120.0, PyPDF2, SQLAlchemy, Alembic, google-genai)
- [x] T004 [P] Initialize Next.js frontend with TypeScript in frontend/package.json (Next.js 15+, React 18, TailwindCSS, Axios, Zustand)
- [x] T005 [P] Configure backend linting/formatting: create backend/.flake8, backend/pyproject.toml for Black/isort
- [x] T006 [P] Configure frontend linting/formatting: create frontend/.eslintrc.json, frontend/.prettierrc
- [x] T007 Create backend/.env.example with all required environment variables (DATABASE_URL, GEMINI_API_KEY, SERVER_PORT, etc.)
- [x] T008 Create frontend/.env.local.example with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_NAME

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T009 Setup PostgreSQL database schema: create backend/alembic/env.py and initial migration with users, documents, summaries, mindmaps, api_logs tables per data-model.md
- [x] T010 [P] Create base configuration management in backend/src/config.py (load from .env, validate settings with Pydantic)
- [x] T011 [P] Implement structured logging utility in backend/src/utils/logger.py (JSON format, context tracking)
- [x] T012 [P] Create error handling framework in backend/src/utils/error_handler.py (ErrorCode enum, AppError class, retry_with_backoff)
- [x] T013 [P] Create validation utilities in backend/src/utils/validators.py (file size, MIME type, filename validation)
- [ ] T014 Create SQLAlchemy base models in backend/src/models/**init**.py (Base, session management)
- [ ] T015 Implement CORS and error middleware in backend/src/middleware/{cors_middleware.py, error_middleware.py}
- [ ] T016 Create FastAPI app initialization in backend/src/main.py (app setup, middleware, health endpoint)
- [ ] T017 Implement health check endpoint in backend/src/api/routes/health.py (database + Gemini API status check)

### Frontend Foundation

- [ ] T018 [P] Create Axios API client with interceptors in frontend/lib/services/api.ts (error handling, response transformation)
- [ ] T019 [P] Setup Zustand state management in frontend/lib/services/store.ts (DocumentState interface, actions)
- [ ] T020 [P] Create TypeScript interfaces in frontend/lib/types/index.ts (Document, Summary, Mindmap, ApiError)
- [ ] T021 [P] Create error formatter utility in frontend/lib/utils/errorFormatter.ts (user-friendly messages)
- [ ] T022 [P] Create client-side validators in frontend/lib/utils/validators.ts (file size, type validation)
- [ ] T023 [P] Setup TailwindCSS configuration in frontend/app/globals.css and frontend/tailwind.config.js
- [ ] T024 [P] Create reusable LoadingSpinner component in frontend/components/LoadingSpinner.tsx
- [ ] T025 [P] Create root layout wrapper in frontend/app/layout.tsx (global providers, error boundary)

### Testing Infrastructure

- [ ] T026 [P] Setup pytest configuration in backend/pytest.ini (async support, coverage settings, test markers)
- [ ] T027 [P] Create backend test fixtures in backend/tests/conftest.py (database, mock Gemini API, sample PDFs)
- [ ] T028 [P] Setup Jest configuration in frontend/jest.config.js (TypeScript, React Testing Library)
- [ ] T029 [P] Create frontend test utilities in frontend/tests/utils/testHelpers.ts (mock store, mock API responses)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload PDF and View Document (Priority: P1) 🎯 MVP

**Goal**: Enable users to upload PDF files and see them appear in the system with basic metadata (filename, upload time, size). This is the foundational capability that enables all other features.

**Independent Test**: Upload a valid PDF file, verify it appears in document list with correct metadata and status="ready" after parsing completes.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T030 [P] [US1] Contract test for POST /api/documents in backend/tests/contract/test_documents_contract.py (validate request/response schema)
- [ ] T031 [P] [US1] Contract test for GET /api/documents in backend/tests/contract/test_documents_contract.py (validate pagination, filtering)
- [ ] T032 [P] [US1] Unit test for PDF parsing in backend/tests/unit/test_pdf_service.py (valid PDF, invalid PDF, corrupted file, metadata extraction)
- [ ] T033 [P] [US1] Unit test for document validation in backend/tests/unit/test_validators.py (file size, MIME type, filename, duplicate hash)
- [ ] T034 [US1] Integration test for upload → parse flow in backend/tests/integration/test_document_flow.py (full upload to ready status)
- [ ] T035 [P] [US1] Frontend unit test for DocumentUpload component in frontend/tests/unit/DocumentUpload.test.tsx
- [ ] T036 [P] [US1] Frontend unit test for DocumentList component in frontend/tests/unit/DocumentList.test.tsx

### Backend Implementation for User Story 1

- [ ] T037 [P] [US1] Create User model in backend/src/models/user.py (id, email, name, timestamps per data-model.md)
- [ ] T038 [P] [US1] Create Document model in backend/src/models/document.py (all fields from data-model.md, relationships, indexes, state validation)
- [ ] T039 [US1] Implement PDF parsing service in backend/src/services/pdf_service.py (PyPDF2 + pdfplumber fallback, text extraction, metadata, page count, 10s timeout)
- [ ] T040 [US1] Implement document CRUD service in backend/src/services/document_service.py (create, list, get, delete, duplicate detection via file_hash)
- [ ] T041 [US1] Create Pydantic schemas in backend/src/api/schemas.py (DocumentUploadRequest, DocumentResponse, DocumentDetail, ErrorResponse)
- [ ] T042 [US1] Implement document upload endpoint in backend/src/api/routes/documents.py POST /api/documents (multipart form, streaming, validation, async parsing queue)
- [ ] T043 [US1] Implement document list endpoint in backend/src/api/routes/documents.py GET /api/documents (pagination, status filtering, user scoping)
- [ ] T044 [US1] Implement document detail endpoint in backend/src/api/routes/documents.py GET /api/documents/{id} (include metadata, page count)
- [ ] T045 [US1] Implement document delete endpoint in backend/src/api/routes/documents.py DELETE /api/documents/{id} (cascade delete)
- [ ] T046 [US1] Add document processing logging with context (document_id, operation, status transitions)

### Frontend Implementation for User Story 1

- [ ] T047 [P] [US1] Create DocumentUpload component in frontend/components/DocumentUpload.tsx (file input, drag-drop, validation, progress bar, error display)
- [ ] T048 [P] [US1] Create DocumentList component in frontend/components/DocumentList.tsx (grid/list view, pagination, status indicators, click to detail)
- [ ] T049 [US1] Create document API service methods in frontend/lib/services/api.ts (uploadDocument, listDocuments, getDocument, deleteDocument)
- [ ] T050 [US1] Create home page with upload and list in frontend/app/page.tsx (integrate DocumentUpload and DocumentList)
- [ ] T051 [US1] Create document detail page in frontend/app/documents/[id]/page.tsx (display metadata, status, creation date, file size, page count)
- [ ] T052 [US1] Add document state management actions in frontend/lib/services/store.ts (setDocuments, setCurrentDocument, loading states)
- [ ] T053 [US1] Add client-side upload validation and user feedback (file size check, type check, error notifications)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can upload PDFs and see them in their document list with complete metadata

---

## Phase 4: User Story 2 - Generate Document Summary (Priority: P1)

**Goal**: Enable users to request AI-powered summaries of uploaded documents. Summaries should be generated within 5 seconds (p95) and capture key concepts in bullet-point format.

**Independent Test**: Upload a PDF (or use existing from US1), click "Generate Summary", verify summary text is returned within 5s and displays correctly with metadata (tokens used, generation time).

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T054 [P] [US2] Contract test for Gemini summary API in backend/tests/contract/test_gemini_contract.py (mock Gemini response, validate prompt format, JSON parsing)
- [ ] T055 [P] [US2] Contract test for POST /api/documents/{id}/summary in backend/tests/contract/test_summaries_contract.py (validate request/response schema)
- [ ] T056 [P] [US2] Unit test for Gemini service in backend/tests/unit/test_gemini_service.py (rate limiting, caching, timeout, retry logic, error handling)
- [ ] T057 [P] [US2] Unit test for summary service in backend/tests/unit/test_summary_service.py (text validation, cache lookup, cost tracking)
- [ ] T058 [US2] Integration test for summary generation flow in backend/tests/integration/test_document_flow.py (document ready → summary generation → cache hit on repeat)
- [ ] T059 [P] [US2] Frontend unit test for SummaryView component in frontend/tests/unit/SummaryView.test.tsx

### Backend Implementation for User Story 2

- [ ] T060 [P] [US2] Create Summary model in backend/src/models/summary.py (all fields from data-model.md, 1:1 relationship with Document, state transitions)
- [ ] T061 [P] [US2] Create APILog model in backend/src/models/api_log.py (audit trail fields, cost tracking, indexes)
- [ ] T062 [US2] Implement LRU cache in backend/src/utils/cache.py (DocumentCache class, 1GB limit, SHA-256 key generation, hit/miss stats)
- [ ] T063 [US2] Implement rate limiter in backend/src/services/gemini_service.py (RateLimiter class, 60 requests/minute, exponential backoff)
- [ ] T064 [US2] Implement Gemini API abstraction in backend/src/services/gemini_service.py (generate_summary method, prompt template per gemini-api.md, timeout 30s, temperature 0.3)
- [ ] T065 [US2] Implement cost tracking middleware in backend/src/services/gemini_service.py (log tokens, calculate cost, update APILog table)
- [ ] T066 [US2] Implement summary service in backend/src/services/summary_service.py (orchestrate: cache check → Gemini call → store result → update status)
- [ ] T067 [US2] Create summary schemas in backend/src/api/schemas.py (SummaryRequest, SummaryResponse with generation_status)
- [ ] T068 [US2] Implement summary generation endpoint in backend/src/api/routes/summaries.py POST /api/documents/{id}/summary (validate document ready, queue generation)
- [ ] T069 [US2] Implement get summary endpoint in backend/src/api/routes/summaries.py GET /api/documents/{id}/summary (return existing or status)
- [ ] T070 [US2] Implement summary download endpoint in backend/src/api/routes/summaries.py GET /api/documents/{id}/summary/download (formats: txt, pdf, markdown)
- [ ] T071 [US2] Add summary validation (non-empty, min 3 bullets, max 10,000 chars)
- [ ] T072 [US2] Add Prometheus metrics for summary operations in backend/src/services/gemini_service.py (summary_duration, tokens_used, cost_usd, cache_hit_ratio)

### Frontend Implementation for User Story 2

- [ ] T073 [P] [US2] Create SummaryView component in frontend/components/SummaryView.tsx (display summary text, metadata: tokens, latency, timestamp, download button)
- [ ] T074 [US2] Add summary API methods in frontend/lib/services/api.ts (generateSummary, getSummary, downloadSummary)
- [ ] T075 [US2] Update document detail page in frontend/app/documents/[id]/page.tsx (add "Generate Summary" button, integrate SummaryView, handle loading/error states)
- [ ] T076 [US2] Add summary state management in frontend/lib/services/store.ts (setSummary, summary loading/error states)
- [ ] T077 [US2] Add status polling for async summary generation in frontend/lib/services/api.ts (poll GET /summary every 2s until complete or failed)
- [ ] T078 [US2] Add user feedback for summary operations (generating spinner, success message, error messages per error codes)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can upload PDFs and generate summaries

---

## Phase 5: User Story 3 - Generate Mindmap from Document (Priority: P2)

**Goal**: Enable users to visualize document structure through interactive hierarchical mindmaps. Mindmaps should be generated within 2 seconds (p95) and display in an interactive tree format.

**Independent Test**: Upload a PDF (or use existing from US1), click "Generate Mindmap", verify JSON mindmap structure is returned within 2s and displays as interactive visual tree.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T079 [P] [US3] Contract test for Gemini mindmap API in backend/tests/contract/test_gemini_contract.py (mock JSON response, validate prompt format, structure validation)
- [ ] T080 [P] [US3] Contract test for POST /api/documents/{id}/mindmap in backend/tests/contract/test_mindmaps_contract.py (validate request/response schema)
- [ ] T081 [P] [US3] Unit test for mindmap JSON validation in backend/tests/unit/test_validators.py (recursive structure, max depth 10, max nodes 500, required fields)
- [ ] T082 [P] [US3] Unit test for mindmap service in backend/tests/unit/test_mindmap_service.py (JSON parsing, validation, cache integration)
- [ ] T083 [US3] Integration test for mindmap generation flow in backend/tests/integration/test_document_flow.py (document ready → mindmap generation → validation)
- [ ] T084 [P] [US3] Frontend unit test for MindmapView component in frontend/tests/unit/MindmapView.test.tsx

### Backend Implementation for User Story 3

- [ ] T085 [P] [US3] Create Mindmap model in backend/src/models/mindmap.py (mindmap_json JSONB field, validation, state transitions, 1:1 relationship with Document)
- [ ] T086 [US3] Implement mindmap JSON validator in backend/src/utils/validators.py (recursive validation, depth check, node count, schema compliance)
- [ ] T087 [US3] Add generate_mindmap method to Gemini service in backend/src/services/gemini_service.py (prompt template per gemini-api.md, timeout 20s, temperature 0.2, JSON parsing)
- [ ] T088 [US3] Implement mindmap service in backend/src/services/mindmap_service.py (orchestrate: cache check → Gemini call → validate JSON → store result)
- [ ] T089 [US3] Create mindmap schemas in backend/src/api/schemas.py (MindmapRequest, MindmapResponse with JSON structure)
- [ ] T090 [US3] Implement mindmap generation endpoint in backend/src/api/routes/mindmaps.py POST /api/documents/{id}/mindmap (validate document ready, queue generation)
- [ ] T091 [US3] Implement get mindmap endpoint in backend/src/api/routes/mindmaps.py GET /api/documents/{id}/mindmap (return JSON structure or status)
- [ ] T092 [US3] Implement mindmap download endpoint in backend/src/api/routes/mindmaps.py GET /api/documents/{id}/mindmap/download (formats: json, png, svg)
- [ ] T093 [US3] Add Prometheus metrics for mindmap operations (mindmap_duration, tokens_used, validation_errors)

### Frontend Implementation for User Story 3

- [ ] T094 [P] [US3] Create MindmapView component in frontend/components/MindmapView.tsx (interactive tree visualization, expand/collapse nodes, node hover details, zoom/pan)
- [ ] T095 [US3] Add mindmap API methods in frontend/lib/services/api.ts (generateMindmap, getMindmap, downloadMindmap)
- [ ] T096 [US3] Update document detail page in frontend/app/documents/[id]/page.tsx (add "Generate Mindmap" button, integrate MindmapView, handle loading/error states)
- [ ] T097 [US3] Add mindmap state management in frontend/lib/services/store.ts (setMindmap, mindmap loading/error states)
- [ ] T098 [US3] Add status polling for async mindmap generation in frontend/lib/services/api.ts (poll GET /mindmap every 2s until complete or failed)
- [ ] T099 [US3] Add user feedback for mindmap operations (generating spinner, success message, error messages)
- [ ] T100 [US3] Add mindmap interaction features (zoom controls, fit-to-screen, node search/highlight)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - complete core feature set

---

## Phase 6: User Story 4 - Manage Multiple Documents (Priority: P2)

**Goal**: Enable users to manage a collection of documents over time with search, filtering, sorting, and organized access to previously generated content.

**Independent Test**: Upload multiple PDFs, generate summaries/mindmaps for some, verify document list shows all documents with correct status, test search/filter functionality, test document retrieval with all associated content.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T101 [P] [US4] Integration test for multi-document workflows in backend/tests/integration/test_document_management.py (upload 5+ docs, query, filter, pagination)
- [ ] T102 [P] [US4] Unit test for document search in backend/tests/unit/test_document_service.py (filename search, date filtering, status filtering)
- [ ] T103 [P] [US4] Frontend E2E test for document management in frontend/tests/e2e/manage-documents.spec.ts (upload, search, filter, delete, view)

### Backend Implementation for User Story 4

- [ ] T104 [P] [US4] Add full-text search index on Document.filename and Document.extracted_text in backend/alembic migration
- [ ] T105 [US4] Extend document service in backend/src/services/document_service.py (add search by filename, filter by date range, sort by various fields)
- [ ] T106 [US4] Add document search endpoint in backend/src/api/routes/documents.py GET /api/documents/search (query parameter, fuzzy matching)
- [ ] T107 [US4] Implement document retention cleanup job in backend/src/services/document_service.py (delete expired documents, cascade to summaries/mindmaps)
- [ ] T108 [US4] Add document statistics endpoint in backend/src/api/routes/documents.py GET /api/documents/stats (count by status, total storage used)

### Frontend Implementation for User Story 4

- [ ] T109 [P] [US4] Add search bar to DocumentList component in frontend/components/DocumentList.tsx (real-time search, clear button)
- [ ] T110 [P] [US4] Add filtering controls to DocumentList component (filter by status, date range, sort options)
- [ ] T111 [US4] Add document search to API service in frontend/lib/services/api.ts (searchDocuments method with debouncing)
- [ ] T112 [US4] Add document deletion confirmation modal in frontend/components/DocumentList.tsx (confirm before delete)
- [ ] T113 [US4] Add bulk selection and actions in frontend/components/DocumentList.tsx (select multiple, bulk delete)
- [ ] T114 [US4] Add document statistics dashboard in frontend/app/page.tsx (total docs, by status, storage used)

**Checkpoint**: At this point, all P1 and P2 user stories are complete - users can manage a full document library

---

## Phase 7: User Story 5 - Export and Share Content (Priority: P3)

**Goal**: Enable users to export generated summaries and mindmaps in multiple formats for use outside the application.

**Independent Test**: Generate a summary and mindmap, export each in all supported formats (summary: txt, pdf, markdown; mindmap: json, png, svg), verify exported files are valid and usable externally.

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T115 [P] [US5] Unit test for export formatters in backend/tests/unit/test_export_service.py (summary to PDF/markdown, mindmap to PNG/SVG)
- [ ] T116 [P] [US5] Integration test for export endpoints in backend/tests/integration/test_export_flow.py (generate, export, verify file format)
- [ ] T117 [P] [US5] Frontend E2E test for export workflows in frontend/tests/e2e/export.spec.ts (download summary, download mindmap, verify files)

### Backend Implementation for User Story 5

- [ ] T118 [P] [US5] Implement summary export service in backend/src/services/export_service.py (format_summary_as_txt, format_summary_as_pdf, format_summary_as_markdown)
- [ ] T119 [P] [US5] Implement mindmap export service in backend/src/services/export_service.py (format_mindmap_as_json, render_mindmap_as_png, render_mindmap_as_svg)
- [ ] T120 [US5] Add export format validation in backend/src/utils/validators.py (validate requested format, content type headers)
- [ ] T121 [US5] Extend summary download endpoint in backend/src/api/routes/summaries.py (support all formats with proper Content-Type headers)
- [ ] T122 [US5] Extend mindmap download endpoint in backend/src/api/routes/mindmaps.py (support all formats with proper Content-Type headers)

### Frontend Implementation for User Story 5

- [ ] T123 [P] [US5] Add export controls to SummaryView in frontend/components/SummaryView.tsx (dropdown: txt/pdf/markdown, download button)
- [ ] T124 [P] [US5] Add export controls to MindmapView in frontend/components/MindmapView.tsx (dropdown: json/png/svg, download button)
- [ ] T125 [US5] Implement client-side download handling in frontend/lib/utils/downloadHelpers.ts (trigger browser download, filename generation)
- [ ] T126 [US5] Add export history tracking in frontend/lib/services/store.ts (track what was exported, when)
- [ ] T127 [US5] Add user feedback for export operations (download progress, success message, error handling)

**Checkpoint**: All user stories (P1, P2, P3) are now complete - full feature set delivered

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Documentation & Deployment

- [ ] T128 [P] Create comprehensive API documentation in backend/docs/api.md (all endpoints, examples, error codes)
- [ ] T129 [P] Create user guide in docs/user-guide.md (screenshots, workflows, troubleshooting)
- [ ] T130 [P] Create developer setup guide in docs/developer-setup.md (local environment, testing, debugging)
- [ ] T131 [P] Write backend Dockerfile in backend/Dockerfile (multi-stage build, production settings)
- [ ] T132 [P] Write frontend Dockerfile in frontend/Dockerfile (Next.js production build)
- [ ] T133 Create docker-compose.yml (backend, frontend, PostgreSQL, optional Redis)
- [ ] T134 Create CI/CD pipeline configuration in .github/workflows/ci.yml (test coverage enforcement, linting, build verification)

### Code Quality & Performance

- [ ] T135 [P] Refactor duplicate code in backend services (DRY principle, extract common patterns)
- [ ] T136 [P] Refactor frontend components (extract reusable UI patterns, shared hooks)
- [ ] T137 [P] Add comprehensive error messages in backend/src/utils/error_messages.py (user-friendly messages per error code)
- [ ] T138 [P] Optimize database queries in backend/src/services/ (add missing indexes, eager loading for relationships)
- [ ] T139 [P] Add database connection pooling configuration in backend/src/config.py (pool size, overflow, timeout)
- [ ] T140 [P] Add frontend performance optimizations (code splitting, lazy loading, image optimization)
- [ ] T141 Implement request/response compression in backend/src/middleware/ (gzip for large JSON responses)
- [ ] T142 Add frontend caching strategy (React Query or SWR for API response caching)

### Monitoring & Observability

- [ ] T143 [P] Create Prometheus metrics dashboard configuration in backend/monitoring/prometheus.yml (all custom metrics)
- [ ] T144 [P] Create Grafana dashboard JSON in backend/monitoring/grafana-dashboard.json (API latency, token usage, cost tracking)
- [ ] T145 [P] Add structured logging to all services (ensure all operations log with context)
- [ ] T146 [P] Implement log aggregation configuration (example: ELK stack or Loki setup docs)
- [ ] T147 Add health check endpoints for all services (detailed status, dependency checks)

### Security & Reliability

- [ ] T148 [P] Implement rate limiting on API endpoints in backend/src/middleware/rate_limit_middleware.py (per-IP, per-user)
- [ ] T149 [P] Add CSRF protection for state-changing operations in backend/src/middleware/
- [ ] T150 [P] Implement API key rotation documentation in docs/security.md (process, automation)
- [ ] T151 [P] Add input sanitization for all user inputs (XSS prevention, SQL injection prevention)
- [ ] T152 [P] Add content security policy headers in frontend/next.config.js
- [ ] T153 Add error recovery mechanisms (retry failed PDF parsing, resume interrupted summaries)
- [ ] T154 Implement graceful shutdown handling in backend/src/main.py (cleanup, drain connections)

### Testing & Validation

- [ ] T155 [P] Add additional unit tests to reach 80% coverage in backend/tests/unit/ (edge cases, error paths)
- [ ] T156 [P] Add E2E tests for critical user journeys in frontend/tests/e2e/ (upload → summary → mindmap → export)
- [ ] T157 [P] Add load testing scenarios in backend/tests/load/ (concurrent uploads, parallel generations)
- [ ] T158 [P] Add contract test for OpenAPI spec validation in backend/tests/contract/ (validate backend-api.yaml matches implementation)
- [ ] T159 Run quickstart.md validation (verify all commands work, update any outdated instructions)
- [ ] T160 Perform security audit (OWASP top 10 check, dependency vulnerabilities)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) completion - can start in parallel with US1
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) completion - can start in parallel with US1/US2
- **User Story 4 (Phase 6)**: Depends on User Story 1 completion (needs document upload infrastructure)
- **User Story 5 (Phase 7)**: Depends on User Stories 2 and 3 completion (needs summaries and mindmaps to export)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ Independent
- **User Story 2 (P1)**: Depends on User Story 1 for document upload, but can develop in parallel with mocked documents ✅ Mostly Independent
- **User Story 3 (P2)**: Depends on User Story 1 for document upload, but can develop in parallel with mocked documents ✅ Mostly Independent
- **User Story 4 (P2)**: Depends on User Story 1 (needs document CRUD infrastructure) ⚠️ Sequential after US1
- **User Story 5 (P3)**: Depends on User Stories 2 and 3 (needs generated content to export) ⚠️ Sequential after US2/US3

### Within Each User Story

1. Tests MUST be written and FAIL before implementation (TDD enforced per Constitution)
2. Backend models before services
3. Backend services before API endpoints
4. Backend API before frontend integration
5. Core implementation before polish
6. Story complete and independently testable before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003-T008 can run in parallel (different config files)

**Phase 2 (Foundational)**:

- Backend tasks T010-T013, T015 can run in parallel (different files)
- Frontend tasks T018-T025 can run in parallel (different files)
- Testing tasks T026-T029 can run in parallel (different files)

**Phase 3 (User Story 1)**:

- Tests T030-T036 can run in parallel (write all tests first)
- Backend models T037-T038 can run in parallel
- Frontend components T047-T048 can run in parallel after backend is ready

**Phase 4 (User Story 2)**:

- Tests T054-T059 can run in parallel (write all tests first)
- Backend models T060-T061 can run in parallel

**Phase 5 (User Story 3)**:

- Tests T079-T084 can run in parallel (write all tests first)

**Phase 8 (Polish)**:

- Documentation tasks T128-T130 can run in parallel
- Dockerfile tasks T131-T132 can run in parallel
- Code quality tasks T135-T142 can run in parallel
- Monitoring tasks T143-T147 can run in parallel
- Security tasks T148-T154 can run in parallel
- Testing tasks T155-T158 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Write all tests first (can be parallelized):
Task T030: Contract test for POST /api/documents
Task T031: Contract test for GET /api/documents
Task T032: Unit test for PDF parsing
Task T033: Unit test for document validation
Task T034: Integration test for upload → parse flow
Task T035: Frontend test for DocumentUpload
Task T036: Frontend test for DocumentList

# Verify all tests FAIL (no implementation yet)

# Launch backend models in parallel:
Task T037: Create User model
Task T038: Create Document model

# After models complete, implement services sequentially:
Task T039: PDF parsing service (needs Document model)
Task T040: Document CRUD service (needs Document model)

# Frontend components in parallel:
Task T047: DocumentUpload component
Task T048: DocumentList component
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only - Core Value Proposition)

This is the recommended path for fastest time-to-value:

1. ✅ Complete Phase 1: Setup (T001-T008) - ~2 hours
2. ✅ Complete Phase 2: Foundational (T009-T029) - ~8 hours - **CRITICAL GATE**
3. ✅ Complete Phase 3: User Story 1 (T030-T053) - ~12 hours - **First working increment**
4. ✅ Complete Phase 4: User Story 2 (T054-T078) - ~10 hours - **MVP COMPLETE** 🎯
5. **STOP and VALIDATE**: Test upload → summary workflow end-to-end
6. Deploy/demo MVP if ready

**Estimated MVP delivery**: ~32 developer-hours (~4 days for one developer)

**MVP Value**: Users can upload PDFs and get AI-powered summaries - core problem solved

### Incremental Delivery (Recommended Production Path)

1. ✅ MVP (US1 + US2) → Test independently → Deploy/Demo
2. ✅ Add User Story 3 (Mindmaps) → Test independently → Deploy/Demo
3. ✅ Add User Story 4 (Multi-document management) → Test independently → Deploy/Demo
4. ✅ Add User Story 5 (Export) → Test independently → Deploy/Demo
5. ✅ Add Phase 8 (Polish) → Production hardening → Deploy to production

Each increment adds value without breaking previous features.

### Parallel Team Strategy (If 3+ Developers Available)

With multiple developers, after Foundational phase:

**Week 1: Core Features (Parallel)**

- Developer A: User Story 1 (Document Upload) - T030-T053
- Developer B: User Story 2 (Summaries) - T054-T078 (can mock document upload initially)
- Developer C: User Story 3 (Mindmaps) - T079-T100 (can mock document upload initially)

**Week 2: Enhancement Features (Parallel)**

- Developer A: User Story 4 (Document Management) - T101-T114
- Developer B: User Story 5 (Export) - T115-T127
- Developer C: Polish & Testing - T128-T160

**Estimated delivery with 3 developers**: ~2 weeks to full feature set

---

## Task Statistics

- **Total Tasks**: 160
- **Phase Breakdown**:

  - Phase 1 (Setup): 8 tasks
  - Phase 2 (Foundational): 21 tasks (CRITICAL - blocks everything)
  - Phase 3 (US1 - Upload): 24 tasks (7 tests + 17 implementation)
  - Phase 4 (US2 - Summary): 25 tasks (6 tests + 19 implementation)
  - Phase 5 (US3 - Mindmap): 22 tasks (6 tests + 16 implementation)
  - Phase 6 (US4 - Management): 14 tasks (3 tests + 11 implementation)
  - Phase 7 (US5 - Export): 13 tasks (3 tests + 10 implementation)
  - Phase 8 (Polish): 33 tasks

- **Parallel Tasks**: 78 tasks marked [P] (~49% can be parallelized within their phase)
- **Test Tasks**: 25 tasks (unit + integration + contract + E2E = ~16% of total)
- **Test Coverage Target**: 80%+ (enforced by CI per Constitution)

- **MVP Task Count**: 29 tasks (Setup + Foundational) + 24 tasks (US1) + 25 tasks (US2) = **78 tasks for MVP**

---

## Validation Checklist

- ✅ All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- ✅ Tasks organized by user story (US1, US2, US3, US4, US5)
- ✅ Each user story has independent test criteria
- ✅ Tests are marked OPTIONAL and explicitly requested in Constitution
- ✅ All tests written BEFORE implementation (TDD enforced)
- ✅ Foundational phase clearly marked as BLOCKING
- ✅ Dependencies section shows story completion order
- ✅ Parallel opportunities identified with [P] marker (78 tasks)
- ✅ MVP scope clearly defined (User Stories 1 + 2 = core value)
- ✅ File paths are specific and follow project structure from plan.md
- ✅ All entities from data-model.md are mapped to tasks
- ✅ All endpoints from backend-api.yaml are mapped to tasks
- ✅ All decisions from research.md are reflected in implementation tasks
- ✅ Constitution principles validated (TDD, SOLID, performance, error handling, API discipline)

---

## Notes

- This feature strictly follows the Constitution: TDD enforced (tests first), SOLID principles (service abstraction), performance targets (<5s summary, <2s mindmap), robust error handling (retry with backoff), API discipline (Gemini abstraction layer with cost tracking)
- Each [P] task operates on different files or has no dependencies, enabling true parallelization
- Each user story delivers independently testable value
- Stop after any phase to validate and demo progress
- Commit after each task or logical group for rollback safety
- All file paths are absolute and follow structure from plan.md
- Backend tests achieve 80%+ coverage per Constitution requirement
- Frontend tests cover critical user journeys and components
- MVP (User Stories 1 + 2) delivers core value: PDF upload + AI summaries
