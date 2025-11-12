<!--
  ============================================================================
  SYNC IMPACT REPORT - Constitution v1.0.0
  ============================================================================

  RATIFICATION: 2025-11-10 (Initial Constitution)

  VERSION CHANGE: N/A → 1.0.0 (initial ratification)
  BUMP TYPE: N/A (new constitution)

  PRINCIPLES CREATED:
  - I. Test-Driven Quality (TDD discipline, coverage, contract testing)
  - II. Code Clarity & Maintainability (DRY, SOLID, reviews, documentation)
  - III. Performance Excellence (API optimization, response times, efficiency)
  - IV. Robust Error Handling (graceful degradation, logging, user feedback)
  - V. API Integration Discipline (Gemini reliability, rate limiting, fallbacks)

  SECTIONS CREATED:
  - Quality Standards (code formatting, testing coverage thresholds)
  - Performance Constraints (response times, resource limits)

  TEMPLATES REQUIRING UPDATES:
  - ✅ .specify/templates/plan-template.md (Constitution Check section references these principles)
  - ✅ .specify/templates/spec-template.md (Requirements must align with principles)
  - ✅ .specify/templates/tasks-template.md (Task organization reflects principle-driven work)

  FOLLOW-UP NOTES:
  - Recommend establishing CI/CD gates for test coverage (target: 80%+)
  - Setup performance monitoring for API calls (track latency, cost per operation)
  - Consider adding linting configuration (.eslintrc, black/flake8 for Python)

  ============================================================================
-->

# Ebook Summary Gemini - Constitution

## Core Principles

### I. Test-Driven Quality (NON-NEGOTIABLE)

Every feature MUST follow strict Test-Driven Development (TDD):

- Tests written and approved by stakeholders → Tests fail → Implementation → Tests pass
- Red-Green-Refactor cycle strictly enforced for all production code
- Unit test coverage MUST exceed 80% of codebase (measured by automated CI gates)
- Contract tests required for all public APIs, Gemini API integrations, and data transformations
- Integration tests mandatory for document upload pipelines, PDF parsing, and end-to-end summarization flows
- No exceptions to TDD—complexity must be justified by stakeholders before test waiver is granted

**Rationale**: Document processing is safety-critical; incorrect summaries or mind maps damage user trust. TDD ensures reliability and prevents regressions.

---

### II. Code Clarity & Maintainability

All code MUST follow DRY (Don't Repeat Yourself) and SOLID principles:

- Single Responsibility: Each module handles one concern (PDF parsing, API calls, formatting, UI rendering)
- Open/Closed: Code open to extension (new document types, summary formats), closed to modification
- Liskov Substitution: Interfaces must be substitutable (e.g., local caching vs. API responses)
- Interface Segregation: Keep interfaces small and focused (not monolithic)
- Dependency Inversion: Depend on abstractions (interfaces), not concrete implementations (e.g., Gemini API layer abstraction)
- Code review required for all PRs; reviewer must verify principle compliance
- Docstrings and inline comments explain intent, not mechanics
- Method names must be self-documenting; rename methods if clarity is unclear
- Max file size 1600 lines; larger files indicate design problems requiring refactoring

**Rationale**: Ebook summarization involves complex logic (PDF extraction, content analysis, formatting). Clarity prevents bugs and enables future contributors to extend features confidently.

---

### III. Performance Excellence

All features MUST optimize for speed, cost, and resource efficiency:

- API call latency: < 5 seconds for summarization, < 2 seconds for mind map generation (p95)
- Memory usage: PDF processing must not exceed 500 MB per document
- Gemini API rate limiting MUST be enforced; queue/batch requests if approaching limits
- Caching MUST be employed for repeated document types and generated outputs
- Database queries must have query plans analyzed; N+1 queries prohibited
- Performance tests REQUIRED for any feature involving external API calls or large data processing
- Measure and log performance metrics for all document processing operations

**Rationale**: Users uploading large documents expect fast feedback. High API costs can undermine project viability; efficient integration is a business requirement.

---

### IV. Robust Error Handling

All error paths MUST be explicit, logged, and communicated clearly to users:

- No silent failures; all errors logged with context (document ID, operation, timestamp, error type)
- Graceful degradation: if mind map generation fails, summary must still be deliverable
- User-facing errors MUST be non-technical and actionable (e.g., "File too large" vs. "BufferError")
- Structured logging required; plain text + JSON support for debugging and monitoring
- Rate limit errors from Gemini API MUST trigger retry logic with exponential backoff (max 3 retries)
- Timeout handling: operations exceeding thresholds must fail fast and retry, not hang
- Error metrics tracked in all error logs (track frequency, types, and recovery success rates)

**Rationale**: Document processing failures are high-stakes; users need confidence that errors are handled, retried, and communicated transparently.

---

### V. API Integration Discipline

All Gemini API interactions MUST be reliable, cost-effective, and observable:

- API abstraction layer required; never call Gemini SDK directly from business logic
- Rate limits checked before each request; requests queued if necessary
- Fallback strategy for API failures: retry with backoff, local cache, or graceful degradation message
- Cost tracking: log tokens consumed per operation; monitor for unexpected spikes
- API contract tests required; mock responses for all Gemini API endpoints used
- Timeout configuration enforced (e.g., 30s max for summary generation, 20s for mind map)
- API key management: keys must be environment variables, never hardcoded; rotation policy documented

**Rationale**: The project depends on a third-party API; discipline in integration prevents cascading failures, cost overruns, and rate limiting issues.

---

## Quality Standards

### Testing Coverage & Gates

- **Minimum Coverage**: 80% for all production code (enforced by CI)
- **Test Types**: Unit (70%), Integration (15%), Contract (10%), E2E (5%)
- **Test Organization**: `/tests/unit/`, `/tests/integration/`, `/tests/contract/`, `/tests/e2e/`
- **CI Compliance**: All tests MUST pass before PRs can merge; flaky tests must be fixed or skipped with justification
- **Performance Tests**: Any operation involving Gemini API MUST have a performance test

### Code Formatting & Style

- Automated formatting required (e.g., Black for Python, Prettier for JavaScript)
- Linting enforced (e.g., Flake8, ESLint) with no warnings allowed in production code
- Type hints/annotations required for all public functions and class methods
- Max line length: 100 characters (except URLs/comments)

---

## Performance Constraints

### Response Time Targets (p95)

| Operation           | Target | Notes                                |
| ------------------- | ------ | ------------------------------------ |
| PDF Upload + Parse  | < 3s   | Depends on file size, max 100 MB     |
| Summary Generation  | < 5s   | Via Gemini API                       |
| Mind Map Generation | < 2s   | Formatted output, cached if possible |
| UI Page Load        | < 2s   | Including all assets                 |

### Resource Limits

- **Memory per PDF**: 500 MB maximum (fail gracefully if exceeded)
- **Concurrent Uploads**: Queue limit enforced; reject if queue exceeds 50 jobs
- **Gemini API Cost**: Track and log per operation; alert if weekly spend exceeds budget
- **Cache Size**: Limit cached results to 1 GB; LRU eviction policy

---

## Governance

### Amendment Process

1. **Propose**: Create an issue documenting the principle change, rationale, and impact
2. **Review**: Two team members must approve the amendment
3. **Document**: Update this constitution, bump version per semantic versioning
4. **Propagate**: Update dependent templates (plan, spec, tasks) with migration notes
5. **Communicate**: Document breaking changes in CHANGELOG and team wiki

### Compliance Review

- All PRs MUST verify compliance with principles during review (checklist item)
- Code must pass automated linting, formatting, and test coverage gates before merge
- Exceptions require explicit stakeholder approval and justification in commit message

### Semantic Versioning for This Constitution

- **MAJOR**: Backward-incompatible principle removals or redefinitions (requires all code refactor)
- **MINOR**: New principle added or existing principle materially expanded (code must adapt within sprint)
- **PATCH**: Clarifications, wording, typo fixes (no code changes required)

### Supporting Documentation

See `.github/README.md` for development quickstart guide and `.specify/templates/` for task/plan/spec templates.

---

**Version**: 1.0.0 | **Ratified**: 2025-11-10 | **Last Amended**: 2025-11-10
