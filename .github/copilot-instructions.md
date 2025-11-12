# Ebook_Summary_gemini Development Guidelines

## Active Features

- **001-pdf-summary-mindmap**: PDF Upload with Summaries and Mindmap Generation (Phase 1 - Design Complete)

## Technology Stack

### Backend

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11
- **Database**: PostgreSQL 15+ (SQLAlchemy ORM, Alembic migrations)
- **LLM Integration**: Google Generative AI (Gemini API)
- **Key Libraries**: PyPDF2 (PDF parsing), pydantic (validation), python-multipart (file uploads)
- **Testing**: pytest, pytest-asyncio, unittest.mock
- **Monitoring**: Prometheus metrics (cost tracking, performance)

### Frontend

- **Framework**: Next.js 15+
- **Language**: TypeScript + React 18
- **State Management**: Zustand
- **HTTP Client**: Axios (with response interceptors for error handling)
- **Styling**: TailwindCSS
- **Testing**: Jest, React Testing Library, Playwright (E2E)

### Infrastructure

- **Deployment**: Docker + Docker Compose (optional)
- **Caching**: In-memory LRU (1GB limit), optional Redis for distributed
- **Error Handling**: Structured JSON logging, graceful degradation
- **Rate Limiting**: Queue-based with exponential backoff

## Project Structure

```text
backend/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── services/
│   ├── api/routes/
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
└── alembic/

frontend/
├── src/
│   ├── pages/
│   ├── components/
│   ├── services/
│   ├── types/
│   └── styles/
└── tests/
```

## Core Principles (Constitution)

1. **Test-Driven Development**: 80%+ coverage enforced by CI
2. **Code Clarity**: SOLID principles, DRY, max 1600 lines/file
3. **Performance**: Summary <5s, Mindmap <2s, Upload <3s (p95 targets)
4. **Error Handling**: Structured logging, retry logic with backoff, graceful degradation
5. **API Discipline**: Abstraction layer for Gemini, rate limiting, cost tracking

## Key Implementation Details

### Data Model

- **User**: Account management (extensible for multi-user)
- **Document**: PDF metadata, upload status, text extraction
- **Summary**: Generated summaries with cost tracking
- **Mindmap**: Hierarchical JSON structure with versioning
- **APILog**: Audit trail for all Gemini API calls

### API Contract

- **Upload**: Multipart form, streaming, async parsing
- **Summary**: REST endpoint with status polling; returns text + metadata
- **Mindmap**: REST endpoint returning JSON structure
- **Health**: /api/health returns database + Gemini API status

### Error Codes

- `INVALID_PDF`: Corrupt or unsupported format
- `FILE_TOO_LARGE`: >100MB
- `RATE_LIMITED`: Gemini API quota; auto-retry with backoff
- `TIMEOUT`: Exceeds 30s for summary, 20s for mindmap
- `DB_ERROR`: Database connection failure

## Development Commands

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Tests
cd backend && pytest tests/ -v --cov=src
cd frontend && npm run test

# Database
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Configuration Files

- `backend/.env`: Database URL, Gemini API key, budget limits
- `frontend/.env.local`: API URL, app name
- `backend/alembic/env.py`: Database migration settings

## Testing Strategy

- **Unit (70%)**: PDF parsing, Gemini mocking, caching, validation
- **Integration (15%)**: Full upload → parse → summary flows
- **Contract (10%)**: Mock Gemini responses, API shape validation
- **E2E (5%)**: Browser-based workflows

## Performance Targets (p95)

| Operation          | Target |
| ------------------ | ------ |
| PDF Upload + Parse | <3s    |
| Summary Generation | <5s    |
| Mindmap Generation | <2s    |
| Page Load          | <2s    |

## Recent Changes

- **001-pdf-summary-mindmap**: Added Phase 0 (Research), Phase 1 (Design):
  - ✅ plan.md (technical context, constitution check, project structure)
  - ✅ research.md (decision rationale for all components)
  - ✅ data-model.md (6 entities, validation rules, relationships)
  - ✅ quickstart.md (setup guide for local development)
  - ✅ backend-api.yaml (OpenAPI 3.0 contract)
  - ✅ gemini-api.md (Gemini integration patterns, retry strategy)

## Next Steps (Phase 2)

- [ ] Implement backend service layer (PDF parsing, Gemini service abstraction)
- [ ] Implement frontend components (upload, document list, summary view, mindmap view)
- [ ] Setup CI/CD pipeline with test coverage gates
- [ ] Deploy development environment (staging)
- [ ] Authentication layer (OAuth2)
