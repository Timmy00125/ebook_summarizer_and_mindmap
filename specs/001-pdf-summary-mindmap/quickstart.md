# Quickstart: PDF Upload with Summaries and Mindmap Generation

**Date**: November 10, 2025  
**Version**: 1.0 (MVP Phase 1)  
**Target**: Get backend + frontend running locally within 15 minutes

---

## Prerequisites

- Python 3.12+ (backend)
- Node.js 18+ (frontend)
- PostgreSQL 16 (database)
- Google Generative AI API key (free tier available at `ai.google.dev`)
- Docker + Docker Compose (optional, for containerized setup)

---

## Architecture Overview

```
┌─────────────────────┐         ┌──────────────────────────┐
│   Next.js Frontend  │         │   FastAPI Backend        │
│   (React 18)        │◄────────┤  (Python 3.12)           │
│                     │ HTTP    │  - PDF parsing           │
│   - Upload form     │         │  - Gemini API calls      │
│   - Document list   │         │  - Database CRUD         │
│   - View summary    │         │  - Error handling        │
│   - View mindmap    │         │  - Rate limiting         │
└─────────────────────┘         └──────────────────────────┘
                                       │
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                   ┌──────▼──────┐        ┌────────▼─────┐
                   │ PostgreSQL  │        │ Gemini API   │
                   │ (localhost) │        │ (cloud)      │
                   └─────────────┘        └──────────────┘
```

---

## Part 1: Backend Setup (FastAPI)

### 1.1 Clone Repository & Setup Python Environment

```bash
cd /path/to/project
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**`requirements.txt` contents**:

```
fastapi==0.120.0
uvicorn[standard]==0.24.0
python-multipart==0.0.6
PyPDF2==4.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
google-genai==0.3.0
python-dotenv==1.0.0
prometheus-client==0.19.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### 1.3 Configure Environment Variables

Create `backend/.env`:

```bash
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ebook_summary

# Gemini API
GEMINI_API_KEY=your_api_key_here  # Get from ai.google.dev

# App Config
MAX_UPLOAD_SIZE_MB=100
DOCUMENT_RETENTION_DAYS=30
DAILY_BUDGET_LIMIT_USD=50.0

# CORS (for local frontend)
CORS_ORIGINS=["http://localhost:3000"]
```

### 1.4 Setup PostgreSQL Database

**Option A: Local PostgreSQL**

```bash
# Install PostgreSQL (if not already installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
# Windows: Download from postgresql.org

# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Ubuntu

# Create database
createdb ebook_summary

# Verify connection
psql -U postgres -d ebook_summary -c "SELECT 1;"
```

**Option B: Docker (Recommended)**

```bash
docker run --name postgres-ebook \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=ebook_summary \
  -p 5432:5432 \
  -d postgres:15

# Update .env with:
# DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/ebook_summary
```

### 1.5 Run Database Migrations

```bash
cd backend
alembic upgrade head
```

**First run**: Alembic will create all tables (users, documents, summaries, mindmaps, api_logs)

### 1.6 Verify Backend Startup

```bash
cd backend
uvicorn src.main:app --reload
```

**Expected output**:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test health endpoint**:

```bash
curl http://localhost:8000/api/health
```

**Expected response**:

```json
{
  "status": "ok",
  "database": "ok",
  "gemini_api": "ok",
  "timestamp": "2025-11-10T12:00:00Z"
}
```

---

## Part 2: Frontend Setup (Next.js)

### 2.1 Install Node Dependencies

```bash
cd frontend
npm install
# or yarn install
```

### 2.2 Configure Environment Variables

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME="PDF Summary & Mindmap"
```

### 2.3 Start Development Server

```bash
cd frontend
npm run dev
# or yarn dev
```

**Expected output**:

```
> next dev
  ▲ Next.js 15.0.0
  - Local:        http://localhost:3000
  - Environment:  .env.local
```

### 2.4 Verify Frontend Loads

Open browser: **http://localhost:3000**

You should see:

- Upload form (file input)
- Document list (initially empty)
- Navigation to settings/help

---

## Part 3: Test the Full Workflow

### 3.1 Upload a PDF

1. Click "Upload PDF" button
2. Select a PDF file (< 100 MB)
3. Wait for confirmation (should see document in list)

**Backend logs** should show:

```
INFO: Document upload received: test.pdf (size: 250KB)
INFO: PDF parsing started (document_id: 1)
INFO: PDF parsing completed (pages: 5, text length: 2500)
```

### 3.2 Generate Summary

1. Click on document in list
2. Click "Generate Summary" button
3. Wait for Gemini API response (should complete within 5 seconds)

**Backend logs** should show:

```
INFO: Summary generation queued (document_id: 1)
INFO: Calling Gemini API... (tokens_input: 450)
INFO: Summary generated (tokens_output: 150, latency: 2.3s)
```

**Frontend** should display:

- Summary text with bullet points
- Metadata: tokens used, generation time

### 3.3 Generate Mindmap

1. Click "Generate Mindmap" button
2. Wait for API response
3. View interactive mindmap visualization

**Frontend** should show:

- Hierarchical tree structure
- Expandable/collapsible nodes
- Node titles and relationships

### 3.4 Download Content

- Click "Download Summary" → saves as `.txt` or `.pdf`
- Click "Download Mindmap" → saves as `.json` or `.png`

---

## Part 4: Verify Testing & Code Quality

### 4.1 Run Backend Tests

```bash
cd backend
pytest tests/ -v --cov=src --cov-report=html
```

**Expected output**:

```
tests/unit/test_pdf_service.py::test_parse_valid_pdf PASSED
tests/unit/test_gemini_service.py::test_summary_generation PASSED
tests/integration/test_document_flow.py::test_upload_and_parse PASSED
...
========================= 45 passed in 2.34s ==========================
```

**Coverage report**: `backend/htmlcov/index.html` (target: ≥80%)

### 4.2 Run Frontend Tests

```bash
cd frontend
npm run test
# or yarn test
```

**Expected output**:

```
PASS  tests/unit/utils.test.ts
PASS  tests/components/DocumentUpload.test.tsx
...
Test Suites: 5 passed, 5 total
Tests: 42 passed, 42 total
```

### 4.3 Check Code Formatting

```bash
# Backend
cd backend
black src/ tests/
flake8 src/ tests/

# Frontend
cd frontend
npm run lint
npm run format
```

---

## Part 5: Troubleshooting

### Issue: Backend can't connect to PostgreSQL

**Solution**:

```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT 1;"

# Check DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL

# Test connection string
PGPASSWORD=mysecretpassword psql -h localhost -U postgres -d ebook_summary -c "SELECT 1;"
```

### Issue: Gemini API returns 401 (Invalid API Key)

**Solution**:

```bash
# Verify API key from ai.google.dev
# Copy key to backend/.env
GEMINI_API_KEY=your_valid_key_here

# Restart backend:
# CTRL+C, then: uvicorn src.main:app --reload
```

### Issue: Frontend can't reach backend API (CORS error)

**Solution**:

```bash
# Verify backend is running on http://localhost:8000
curl http://localhost:8000/api/health

# Verify frontend .env.local has correct URL
cat frontend/.env.local | grep NEXT_PUBLIC_API_URL

# Verify backend CORS config includes http://localhost:3000
cat backend/.env | grep CORS_ORIGINS
```

### Issue: PDF parsing fails or extracts no text

**Possible causes**:

1. PDF is scanned image (no text layer) → Use OCR (Phase 2)
2. PDF is password-protected → User must remove password
3. PDF is corrupt → User uploads different file

**Current workaround**: Return error message to user; don't attempt extraction

---

## Part 6: Project Structure Reference

### Backend Directory

```
backend/
├── src/
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Settings (from .env)
│   ├── models/
│   │   ├── document.py         # SQLAlchemy ORM models
│   │   ├── summary.py
│   │   └── mindmap.py
│   ├── services/
│   │   ├── pdf_service.py      # PDF parsing logic
│   │   ├── gemini_service.py   # Gemini API abstraction
│   │   ├── summary_service.py
│   │   └── document_service.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── documents.py    # /api/documents/* endpoints
│   │   │   ├── summaries.py    # /api/documents/*/summary
│   │   │   └── mindmaps.py     # /api/documents/*/mindmap
│   │   └── schemas.py          # Pydantic request/response models
│   └── utils/
│       ├── error_handler.py
│       ├── logger.py
│       └── validators.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── alembic/
│   └── versions/               # Database migrations
├── .env                        # Environment variables
├── requirements.txt
└── README.md
```

### Frontend Directory

```
frontend/
├── src/
│   ├── pages/
│   │   ├── index.tsx           # Home page (document list)
│   │   ├── documents/
│   │   │   └── [id].tsx        # Document detail page
│   │   └── _app.tsx            # App wrapper
│   ├── components/
│   │   ├── DocumentUpload.tsx
│   │   ├── DocumentList.tsx
│   │   ├── SummaryView.tsx
│   │   └── MindmapView.tsx
│   ├── services/
│   │   ├── api.ts              # Axios client
│   │   └── store.ts            # Zustand state
│   ├── types/
│   │   └── index.ts            # TypeScript types
│   └── styles/
│       └── globals.css
├── tests/
│   ├── unit/
│   └── e2e/
├── .env.local
├── package.json
└── README.md
```

---

## Part 7: Next Steps

### Immediate (Phase 1 completion):

- [ ] Run full test suite (backend + frontend)
- [ ] Verify 80%+ code coverage
- [ ] Deploy locally to verify end-to-end flow

### Phase 2 (Production readiness):

- [ ] Add authentication (OAuth2, JWT)
- [ ] Multi-user document organization
- [ ] Advanced caching (Redis)
- [ ] Performance monitoring (Prometheus + Grafana)
- [ ] OCR support for scanned PDFs
- [ ] Version history for summaries/mindmaps
- [ ] Export formats (PDF, Markdown for summaries; SVG, PNG for mindmaps)

### Phase 3 (Advanced features):

- [ ] Real-time collaboration (WebSocket)
- [ ] Custom prompt templates
- [ ] Document sharing and permissions
- [ ] AI-powered Q&A on documents
- [ ] Integration with note-taking apps (Notion, Obsidian)

---

## Quick Reference Commands

### Start Development Environment

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Database (if using local PostgreSQL)
# Already running or: docker run -d -p 5432:5432 --name postgres-ebook ...
```

### Run Tests

```bash
# Backend unit tests
cd backend && pytest tests/unit/ -v

# Backend all tests with coverage
cd backend && pytest tests/ -v --cov=src --cov-report=term-missing

# Frontend tests
cd frontend && npm run test

# E2E tests (requires backend + frontend running)
cd frontend && npm run test:e2e
```

### Check Code Quality

```bash
# Backend
cd backend
black src/ --check
flake8 src/ --max-line-length=100
mypy src/ --strict

# Frontend
cd frontend
npm run lint
npm run type-check
```

### Database Management

```bash
# Create migration
cd backend
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Connect to database
psql -U postgres -d ebook_summary
```

---

## Success Criteria

✅ **MVP Complete When**:

- Backend health check returns `ok` for database + Gemini API
- Frontend loads without errors
- Can upload PDF → document appears in list
- Can generate summary within 5 seconds
- Can generate mindmap within 2 seconds
- All tests pass with ≥80% coverage
- No console errors in backend or frontend
- CORS working (frontend can call backend)

---

## Support & Debugging

**Backend Logs**: `backend/logs/app.log`  
**Frontend Logs**: Browser DevTools Console (F12)  
**Database**: `psql -d ebook_summary`

**Debug Mode** (if stuck):

```bash
# Backend: Extra verbose logging
cd backend
LOGLEVEL=DEBUG uvicorn src.main:app --reload

# Frontend: React DevTools
# Install: https://react-devtools-tutorial.vercel.app/
```

---

**Welcome! You're ready to start development. 🚀**
