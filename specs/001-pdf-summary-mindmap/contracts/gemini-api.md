# Gemini API Integration Contract

**Date**: November 10, 2025  
**Purpose**: Document expected Gemini API request/response formats and error handling strategy

---

## Overview

The backend integrates with Google Generative AI (Gemini API) through a service abstraction layer. This contract ensures:

- Consistent prompt formatting for reproducibility
- Error handling with retry logic and rate limiting
- Cost tracking and token optimization
- Mock-friendly interface for testing

---

## 1. Summary Generation Contract

### Request

**Operation**: Generate concise summary from document text

**Prompt Template**:

```
Summarize the following document in clear, concise bullet points.
Focus on key concepts, findings, and conclusions.
Output 5-10 bullets, each 1-2 sentences.

Document:
{DOCUMENT_TEXT}

Summary:
```

**Constraints**:

- Max input tokens: 30,000 (Gemini's typical token limit for long context)
- Max output tokens: configurable, default 1,000
- Temperature: 0.3 (low creativity for factual summaries)
- Timeout: 30 seconds (p95 target from Constitution)

**Code Example**:

```python
# backend/src/services/gemini_service.py
async def generate_summary(
    self,
    document_text: str,
    max_output_tokens: int = 1000
) -> str:
    """
    Generate summary via Gemini API.

    Args:
        document_text: Full extracted text from PDF
        max_output_tokens: Max summary length

    Returns:
        Summary text

    Raises:
        GeminiAPIError: On API failure (retried by caller)
        TimeoutError: If exceeds 30s
    """
    prompt = f"""Summarize the following document in clear, concise bullet points.
Focus on key concepts, findings, and conclusions.
Output 5-10 bullets, each 1-2 sentences.

Document:
{document_text}

Summary:"""

    response = await self.client.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=max_output_tokens,
            candidate_count=1,  # Single best response
        ),
        safety_settings={
            genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED:
                genai.types.HarmBlockThreshold.BLOCK_NONE,
        },
        timeout=30  # Seconds
    )

    # Extract text; handle empty responses
    summary_text = response.text.strip()
    if not summary_text:
        raise GeminiAPIError("Empty response from Gemini API")

    return summary_text
```

### Response

**Format**: Plain text with bullet points

**Example**:

```
• Key finding 1: This document discusses the importance of structured data management...
• Key finding 2: Performance optimization should prioritize database indexing...
• Key finding 3: The authors recommend a phased implementation approach...
```

**Validation**:

- Response must be non-empty
- Response must contain at least 3 bullet points
- Response must be <10,000 characters (prevent excessively verbose output)

**Error Handling**:

- Empty response: Retry with increased temperature (0.5)
- Malformed response: Log and return as-is (graceful degradation)
- API error: Retry with exponential backoff (max 3 attempts)

---

## 2. Mindmap Generation Contract

### Request

**Operation**: Generate hierarchical mindmap from document text

**Prompt Template**:

```
Convert the following document into a hierarchical mindmap structure.
Return ONLY valid JSON with no markdown markers, no code blocks, no additional text.

Format:
{
  "title": "Document title or main topic",
  "children": [
    {
      "title": "Main concept 1",
      "children": [
        {"title": "Subtopic 1.1", "children": []},
        {"title": "Subtopic 1.2", "children": []}
      ]
    },
    {
      "title": "Main concept 2",
      "children": [...]
    }
  ]
}

IMPORTANT:
- Each node must have "title" (string) and "children" (array)
- Max 10 hierarchy levels
- Max 500 total nodes
- Be specific and detailed with titles (3-10 words each)
- Preserve document's original structure and terminology

Document:
{DOCUMENT_TEXT}

JSON:
```

**Constraints**:

- Max input tokens: 30,000
- Max output tokens: configurable, default 2,000 (JSON can be verbose)
- Temperature: 0.2 (very low for structured output)
- Timeout: 20 seconds (faster than summary; structured format)

**Code Example**:

````python
async def generate_mindmap(
    self,
    document_text: str,
    max_output_tokens: int = 2000
) -> dict:
    """
    Generate mindmap via Gemini API.

    Returns:
        Parsed JSON dict with structure:
        {
            "title": str,
            "children": [...]  # Recursive structure
        }

    Raises:
        GeminiAPIError: On API failure or invalid JSON
        ValidationError: If structure violates constraints
    """
    prompt = f"""Convert the following document into a hierarchical mindmap structure...
{document_text}

JSON:"""

    response = await self.client.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,  # Low creativity
            max_output_tokens=max_output_tokens,
        ),
        timeout=20
    )

    json_text = response.text.strip()

    # Remove markdown markers if present
    json_text = json_text.replace("```json", "").replace("```", "")

    try:
        mindmap_obj = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise GeminiAPIError(f"Invalid JSON from Gemini: {str(e)}")

    # Validate structure
    self._validate_mindmap_structure(mindmap_obj)

    return mindmap_obj

def _validate_mindmap_structure(self, obj: dict, depth: int = 0) -> None:
    """Validate mindmap JSON structure against constraints."""
    if depth > 10:
        raise ValidationError("MINDMAP_TOO_DEEP", "Max 10 hierarchy levels")

    if "title" not in obj or not isinstance(obj["title"], str):
        raise ValidationError("INVALID_NODE", "Missing or invalid 'title'")

    if "children" not in obj or not isinstance(obj["children"], list):
        raise ValidationError("INVALID_NODE", "Missing or invalid 'children'")

    if len(obj["children"]) > 100:
        raise ValidationError("TOO_MANY_CHILDREN", "Max 100 children per node")

    for child in obj["children"]:
        self._validate_mindmap_structure(child, depth + 1)
````

### Response

**Format**: Valid JSON (no markdown formatting)

**Example**:

```json
{
  "title": "Machine Learning Best Practices",
  "children": [
    {
      "title": "Data Preparation",
      "children": [
        { "title": "Data Cleaning and Normalization", "children": [] },
        { "title": "Train/Test Split Strategy", "children": [] },
        { "title": "Handling Missing Values", "children": [] }
      ]
    },
    {
      "title": "Model Training",
      "children": [
        { "title": "Feature Engineering", "children": [] },
        { "title": "Hyperparameter Tuning", "children": [] },
        { "title": "Cross-Validation Techniques", "children": [] }
      ]
    }
  ]
}
```

**Validation**:

- Must be valid JSON
- Root object must have `title` and `children`
- All nodes must follow same structure
- Max depth: 10 levels
- Max nodes: 500
- No malformed/dangling references

**Error Handling**:

- Invalid JSON: Retry with more explicit prompt + lower temperature
- Invalid structure: Log detailed error; queue for manual review
- Excessively nested: Trim to 10 levels; warn user
- API error: Retry with exponential backoff

---

## 3. Rate Limiting & Request Queuing

### Rate Limit Strategy

**Assumption**: Gemini API allows 60 requests/minute (conservative estimate; adjust per quota)

**Enforcement**:

```python
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.request_times = []  # Circular buffer

    async def acquire(self) -> None:
        """Wait if rate limit approaching."""
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) >= self.rpm:
            # Wait until oldest request expires
            wait_time = 60 - (now - self.request_times[0])
            await asyncio.sleep(wait_time)

        self.request_times.append(time.time())
```

### Request Queuing

**Pattern**: FIFO async queue with concurrency limit

```python
class RequestQueue:
    def __init__(self, max_concurrent: int = 3):
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.workers = []

    async def enqueue(self, document_id: int, operation: str) -> None:
        """Add request to queue."""
        await self.queue.put({"document_id": document_id, "operation": operation})

    async def process_queue(self) -> None:
        """Worker: process queue items with rate limiting."""
        while True:
            item = await self.queue.get()
            async with self.semaphore:
                await self.rate_limiter.acquire()
                try:
                    if item["operation"] == "summarize":
                        await self._process_summary(item["document_id"])
                    else:
                        await self._process_mindmap(item["document_id"])
                finally:
                    self.queue.task_done()
```

---

## 4. Error Handling & Retry Strategy

### Retryable Errors

| Error               | HTTP Status | Retry? | Max Attempts | Backoff                   |
| ------------------- | ----------- | ------ | ------------ | ------------------------- |
| RATE_LIMITED        | 429         | Yes    | 3            | Exponential (2^n seconds) |
| TIMEOUT             | -           | Yes    | 3            | Exponential               |
| INTERNAL_ERROR      | 500         | Yes    | 3            | Exponential               |
| SERVICE_UNAVAILABLE | 503         | Yes    | 3            | Exponential               |

### Non-Retryable Errors

| Error                       | HTTP Status           | Action                 |
| --------------------------- | --------------------- | ---------------------- |
| INVALID_API_KEY             | 401                   | Fail fast; alert ops   |
| UNSUPPORTED_MODEL           | 400                   | Fail fast; update code |
| QUOTA_EXCEEDED (hard limit) | 429 (after 3 retries) | Fail; alert user + ops |

### Retry Implementation

```python
async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """Exponential backoff retry decorator."""
    for attempt in range(max_retries):
        try:
            return await func()
        except (TimeoutError, RateLimitError) as e:
            if attempt == max_retries - 1:
                raise GeminiAPIError(f"Failed after {max_retries} retries: {str(e)}")

            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
        except NonRetryableError as e:
            raise  # Fail immediately
```

---

## 5. Cost Tracking

### Token Accounting

**Every API response includes**:

- `tokens_input`: Input tokens consumed
- `tokens_output`: Output tokens consumed

**Logging**:

```python
async def _log_api_call(
    self,
    operation: str,
    tokens_input: int,
    tokens_output: int,
    latency_ms: int,
    status: str,
    document_id: int = None
) -> None:
    """Log API call for cost tracking."""
    # Pricing (as of Nov 2024; verify with Google)
    price_input = 0.00075 / 1000  # $0.75 per 1M tokens
    price_output = 0.003 / 1000    # $3.00 per 1M tokens

    cost_usd = (tokens_input * price_input) + (tokens_output * price_output)

    log_entry = APILog(
        operation=operation,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        status=status,
        document_id=document_id
    )
    db.add(log_entry)
    await db.commit()

    # Daily budget check
    daily_cost = await self._calculate_daily_cost()
    if daily_cost > DAILY_BUDGET_LIMIT:
        logger.warning(f"Daily budget exceeded: ${daily_cost:.2f}")
```

---

## 6. Testing: Contract Mocking

### Mock Gemini Client

```python
# tests/contract/test_gemini_contract.py
import pytest
from unittest.mock import AsyncMock

class MockGeminiResponse:
    def __init__(self, text: str):
        self.text = text

@pytest.fixture
def mock_gemini_client(monkeypatch):
    """Mock Gemini API responses."""
    mock_client = AsyncMock()

    async def mock_generate_content(prompt: str, **kwargs):
        if "Summarize" in prompt:
            return MockGeminiResponse("• Key finding 1\n• Key finding 2")
        elif "mindmap" in prompt.lower():
            return MockGeminiResponse(
                json.dumps({
                    "title": "Test Doc",
                    "children": []
                })
            )

    mock_client.generate_content = mock_generate_content
    monkeypatch.setattr("backend.services.gemini_service.genai.Client", mock_client)
    return mock_client

@pytest.mark.asyncio
async def test_summary_generation(mock_gemini_client):
    service = GeminiService(api_key="test")
    result = await service.generate_summary("test document")
    assert result == "• Key finding 1\n• Key finding 2"

@pytest.mark.asyncio
async def test_rate_limiting_blocks_request(mock_gemini_client):
    service = GeminiService(api_key="test")
    # Make 60 requests (hit limit)
    for i in range(60):
        service.rate_limiter.request_times.append(time.time())

    # Next request should wait
    start = time.time()
    await service.rate_limiter.acquire()
    elapsed = time.time() - start
    assert elapsed >= 1.0  # Should wait ~60 seconds
```

---

## 7. Fallback Strategy

### If Gemini API Fails

**Graceful Degradation**:

1. **Summary fails** → Return cached summary if available; else notify user "Summary temporarily unavailable"
2. **Mindmap fails** → Return basic skeleton mindmap (just document title); notify user
3. **Both fail** → Return document metadata only; suggest retry later

**User Messages**:

```python
GEMINI_ERROR_MESSAGES = {
    "RATE_LIMITED": "Service busy. Retrying in a moment...",
    "TIMEOUT": "Generation took too long. Please retry.",
    "TEMPORARY_ERROR": "Temporary service error. Please retry.",
    "QUOTA_EXCEEDED": "Monthly quota exceeded. Retry tomorrow.",
    "INVALID_API_KEY": "System configuration error. Please contact support.",
}
```

---

## Summary

**Contract Ensures**:

- ✅ Reproducible results (fixed prompts, low temperature)
- ✅ Type safety (validated JSON responses)
- ✅ Cost visibility (every call logged)
- ✅ Reliability (retry logic, rate limiting, graceful degradation)
- ✅ Testability (mockable interface, contract tests)

**Next Phase**: Implement service layer following this contract; verify via contract tests.
