# Ebook_Summary_gemini AI Agents

## Overview

This document defines specialized AI agents and their responsibilities within the Ebook_Summary_gemini project. Each agent has specific capabilities, constraints, and operational guidelines to ensure efficient development, testing, and maintenance.

## Agent Roster

### 1. Architecture Agent

**Role**: System Design & Technical Planning  
**Capabilities**:

- Full-stack architecture review (FastAPI + Next.js)
- Database schema design and optimization
- API contract definition and validation
- Performance bottleneck identification
- Scalability planning

**Constraints**:

- Must follow SOLID principles
- Enforce DRY across all designs
- Max 1600 lines per file recommendation
- All changes require test coverage planning

**Invocation Triggers**:

- New feature specification requests
- Performance optimization needs
- Major refactoring proposals
- Database schema changes
- API endpoint additions

**Output Format**:

```markdown
## Proposed Architecture

- Component breakdown
- Data flow diagrams
- API contracts
- Database migrations needed
- Testing strategy
- Performance impact assessment
```

---

### 2. Backend Developer Agent

**Role**: FastAPI Development & Python Implementation  
**Capabilities**:

- FastAPI route implementation
- SQLAlchemy model creation
- Alembic migration generation
- Gemini API integration
- PDF parsing with PyPDF2
- Async/await patterns
- Pydantic validation schemas

**Technology Stack**:

- Python 3.12
- FastAPI 0.120.0
- PostgreSQL 16 + SQLAlchemy
- Alembic for migrations
- Google Generative AI (Gemini)

**Constraints**:

- Must read `python.instructions.md` and `FastAPI.instructions.md` before coding
- Follow PEP 8 and type hints required
- Docstrings mandatory for all public methods
- Error handling with structured logging
- Rate limiting and retry logic for external APIs
- Cost tracking for all Gemini API calls

**Testing Requirements**:

- Unit tests with pytest
- Mock Gemini API responses
- 80%+ coverage enforced
- Integration tests for database operations

**Example Tasks**:

- Implement PDF upload endpoint with streaming
- Create summary generation service with caching
- Add Prometheus metrics for cost tracking
- Optimize database queries with SQLAlchemy

---

### 3. Frontend Developer Agent

**Role**: Next.js + React Implementation  
**Capabilities**:

- Next.js 15+ page and component creation
- TypeScript + React 18 development
- Zustand state management
- Axios HTTP client configuration
- TailwindCSS styling
- Form validation and error handling
- Responsive design implementation

**Technology Stack**:

- Next.js 15+
- TypeScript + React 18
- Zustand (state management)
- Axios (HTTP client)
- TailwindCSS

**Constraints**:

- Must read `Nextjs.instructions.md` before coding
- TypeScript strict mode enabled
- Component prop types required
- Accessibility standards (WCAG 2.1 AA)
- Error boundaries for all async operations
- Loading states for all API calls

**Testing Requirements**:

- Jest unit tests
- React Testing Library
- Playwright E2E tests
- Component accessibility tests

**Example Tasks**:

- Create PDF upload component with progress
- Implement summary display with retry logic
- Build mindmap visualization component
- Add error toast notifications

---

### 4. QA & Testing Agent

**Role**: Test Creation & Quality Assurance  
**Capabilities**:

- Test suite design (unit, integration, contract, E2E)
- pytest test implementation
- Jest + React Testing Library tests
- Playwright E2E scenarios
- Mock data generation
- Coverage analysis
- Performance testing

**Testing Strategy**:
| Test Type | Coverage | Focus Areas |
|--------------|----------|--------------------------------------|
| Unit | 70% | PDF parsing, caching, validation |
| Integration | 15% | Upload → parse → summary flows |
| Contract | 10% | Gemini API shape validation |
| E2E | 5% | Browser-based user workflows |

**Constraints**:

- 80%+ total coverage enforced
- All critical paths covered
- Mock external API calls
- No flaky tests allowed
- Performance assertions included

**Example Tasks**:

- Write unit tests for PDF parsing service
- Create integration test for summary generation
- Implement E2E test for upload workflow
- Add contract test for Gemini API response

---

### 5. DevOps Agent

**Role**: Infrastructure, Deployment & Monitoring  
**Capabilities**:

- Docker + Docker Compose configuration
- Database migration management
- Environment configuration
- Logging and monitoring setup
- Performance optimization
- CI/CD pipeline configuration

**Infrastructure Stack**:

- Docker + Docker Compose
- PostgreSQL 16
- Redis (optional caching)
- Prometheus metrics
- Structured JSON logging

**Constraints**:

- Environment variables for all secrets
- Health check endpoints required
- Graceful shutdown handling
- Resource limits defined
- Backup strategy documented

**Example Tasks**:

- Create Docker Compose setup
- Configure Alembic migrations
- Set up Prometheus metrics
- Implement health check endpoint
- Configure rate limiting

---

### 6. API Integration Agent

**Role**: External API Management & Integration  
**Capabilities**:

- Gemini API integration
- Rate limiting implementation
- Retry logic with exponential backoff
- Cost tracking and budget management
- API abstraction layer design
- Error handling and fallback strategies

**API Management**:

- **Primary**: Google Generative AI (Gemini)
- **Rate Limiting**: Queue-based with backoff
- **Caching**: LRU (1GB limit), optional Redis
- **Budget**: Cost tracking per request
- **Monitoring**: Prometheus metrics

**Error Codes**:
| Code | Description | Action |
|----------------|--------------------------------------|-------------------------|
| RATE_LIMITED | Gemini API quota exceeded | Auto-retry with backoff |
| TIMEOUT | Request exceeds time limit | Return cached or error |
| INVALID_API_KEY| Authentication failure | Alert admin |
| API_ERROR | Gemini service error | Log and retry |

**Constraints**:

- Abstract all external API calls
- Implement circuit breaker pattern
- Log all API interactions
- Track costs per operation
- Graceful degradation required

**Example Tasks**:

- Implement Gemini API service with retry
- Add cost tracking middleware
- Create caching layer for summaries
- Build rate limiter with queue

---

### 7. Code Review Agent

**Role**: Code Quality & Standards Enforcement  
**Capabilities**:

- SOLID principles validation
- DRY principle enforcement
- Code complexity analysis
- Security vulnerability scanning
- Performance review
- Documentation completeness check

**Review Checklist**:

- [ ] Follows project coding standards
- [ ] Type hints present (Python) / TypeScript types (frontend)
- [ ] Docstrings/comments for complex logic
- [ ] Error handling implemented
- [ ] Tests included (80%+ coverage)
- [ ] No code duplication
- [ ] File size < 1600 lines
- [ ] Performance considerations noted
- [ ] Security best practices followed

**Constraints**:

- Must reference `READ_BEFORE_TOUCING_CODE.instructions.md`
- Flag any anti-patterns
- Suggest refactoring opportunities
- Verify test coverage
- Check for breaking changes

**Output Format**:

```markdown
## Code Review: [Feature/PR Name]

### Approval Status: ✅ Approved | ⚠️ Needs Changes | ❌ Rejected

### Summary

- Brief overview of changes

### Findings

#### Critical Issues

- List blocking issues

#### Suggestions

- Improvement recommendations

#### Positive Notes

- Well-implemented aspects

### Coverage: [X]%

### Performance Impact: [Assessment]
```

---

### 8. Documentation Agent

**Role**: Documentation Creation & Maintenance  
**Capabilities**:

- API documentation generation
- User guide creation
- Code comment enhancement
- README updates
- Migration guide writing
- Specification documentation

**Documentation Standards**:

- Markdown format
- Clear examples included
- Up-to-date with codebase
- API contracts in OpenAPI/Swagger
- Inline code documentation (docstrings)

**Constraints**:

- Keep docs synced with code
- Include practical examples
- Document all public APIs
- Explain error codes
- Provide configuration examples

**Example Tasks**:

- Update API documentation after endpoint changes
- Create user guide for PDF upload feature
- Document Gemini API integration
- Write migration guide for database changes
- Generate OpenAPI specification

---

## Agent Coordination

### Multi-Agent Workflows

#### Feature Development Flow

1. **Architecture Agent**: Design system components
2. **Backend Developer Agent**: Implement API endpoints
3. **Frontend Developer Agent**: Build UI components
4. **QA Agent**: Create test suite
5. **Code Review Agent**: Validate implementation
6. **Documentation Agent**: Update docs
7. **DevOps Agent**: Deploy and monitor

#### Bug Fix Flow

1. **QA Agent**: Reproduce and document bug
2. **Backend/Frontend Agent**: Implement fix
3. **QA Agent**: Verify fix with tests
4. **Code Review Agent**: Review changes
5. **DevOps Agent**: Deploy hotfix

#### Performance Optimization Flow

1. **Architecture Agent**: Identify bottlenecks
2. **API Integration Agent**: Optimize external calls
3. **Backend/Frontend Agent**: Implement optimizations
4. **QA Agent**: Benchmark performance
5. **DevOps Agent**: Monitor production metrics

---

## Performance Targets (p95)

All agents must ensure changes meet these targets:

| Operation          | Target | Responsible Agent(s)     |
| ------------------ | ------ | ------------------------ |
| PDF Upload + Parse | <3s    | Backend, DevOps          |
| Summary Generation | <5s    | Backend, API Integration |
| Mindmap Generation | <2s    | Backend, API Integration |
| Page Load          | <2s    | Frontend, DevOps         |

---

## Common Commands by Agent

### Backend Developer

```bash
cd backend
conda activate ebook-summary
uvicorn src.main:app --reload
pytest tests/ -v --cov=src
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Frontend Developer

```bash
cd frontend
npm run dev
npm run test
npm run build
npm run lint
```

### QA Agent

```bash
# Backend tests
cd backend && pytest tests/ -v --cov=src --cov-report=html

# Frontend tests
cd frontend
npm run test -- --coverage
npm run test:e2e
```

### DevOps Agent

```bash
docker-compose up -d
docker-compose logs -f backend
docker-compose exec backend alembic upgrade head
docker-compose down
```

---

## Agent Activation

To activate a specific agent for a task, use the following format:

```
@[Agent Name]: [Task Description]

Context:
- Relevant files
- Current state
- Expected outcome

Constraints:
- Specific requirements
- Performance targets
- Testing requirements
```

**Example**:

```
@Backend Developer Agent: Implement PDF upload endpoint

Context:
- Need to handle multipart/form-data
- Max file size: 100MB
- Store metadata in PostgreSQL
- Extract text asynchronously

Constraints:
- Must stream files (no memory loading)
- Add progress tracking
- Implement retry logic
- 80%+ test coverage required
- Complete within 3s (p95)
```

---

## Agent Best Practices

### All Agents Must:

1. **Read instruction files** before making changes
2. **Follow SOLID and DRY principles**
3. **Maintain test coverage** (80%+)
4. **Document all changes** clearly
5. **Consider performance impact**
6. **Handle errors gracefully**
7. **Provide clear explanations** of changes
8. **Respect file size limits** (1600 lines)

### Communication Protocol

- **Be explicit** about what you're doing and why
- **List your plan** before execution
- **Mention side effects** of changes
- **Flag breaking changes** immediately
- **Reference relevant specs** and docs

### Quality Gates

- ✅ Tests pass and coverage maintained
- ✅ No linting errors
- ✅ Performance targets met
- ✅ Documentation updated
- ✅ Code review approved
- ✅ No security vulnerabilities

---

## Revision History

| Version | Date       | Changes                   | Author |
| ------- | ---------- | ------------------------- | ------ |
| 1.0.0   | 2025-01-14 | Initial agent definitions | System |

---

## References

- [Copilot Instructions](./copilot-instructions.md)
- [Feature Spec: 001-pdf-summary-mindmap](../specs/001-pdf-summary-mindmap/spec.md)
- [Backend API Contract](../specs/001-pdf-summary-mindmap/contracts/backend-api.yaml)
- [READ_BEFORE_TOUCHING_CODE.instructions.md](vscode-userdata:/home/timmy/.config/Code/User/prompts/READ_BEFORE_TOUCING_CODE.instructions.md)
