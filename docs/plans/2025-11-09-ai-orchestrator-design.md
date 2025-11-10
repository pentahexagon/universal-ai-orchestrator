# Universal AI Orchestrator - Design Document

**Date:** 2025-11-09
**Version:** 1.0
**Status:** Approved

## Executive Summary

The Universal AI Orchestrator is a consensus-building system that queries multiple AI services (Gemini, ChatGPT, Claude) for diverse perspectives, then synthesizes them into intelligent unified recommendations. The system operates as a Notion-integrated workflow automation tool, monitoring an Inbox database for questions and publishing comprehensive analysis results.

### Key Requirements

- **Use Case:** Consensus building across 3 AI agents
- **Integration:** Full Notion workflow (input + output)
- **Synthesis:** AI-powered (Claude) intelligent merging
- **Constraints:** Cost-conscious, fast, reliable, simple deployment
- **Monitoring:** 30-60 second polling interval

## Architecture Overview

### Architectural Pattern: Plugin-Based Orchestration

The system uses a plugin-based architecture with async orchestration for optimal balance between simplicity, flexibility, and performance.

**Core Principles:**
- **Plugin System:** Each AI agent implements a standard interface
- **Async Execution:** Parallel processing for speed
- **Sequential Context Building:** Each AI receives previous responses
- **Config-Driven:** YAML configuration for flexibility
- **Separation of Concerns:** Clear boundaries between components

### High-Level Components

```
┌─────────────────────────────────────────────────────┐
│                 Notion Inbox DB                      │
│           (Status: pending/processing/               │
│                   completed/failed)                  │
└──────────────────┬──────────────────────────────────┘
                   │ Poll every 30-60s
                   ▼
┌─────────────────────────────────────────────────────┐
│            Notion Watcher Service                    │
│  - Polls for pending questions                      │
│  - Manages processing state                         │
│  - Concurrency control (semaphore)                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│               Orchestrator (Core)                    │
│  - Central coordinator                              │
│  - Dispatches to AI agents                          │
│  - Manages synthesis                                │
│  - Error aggregation                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ├──────────┬──────────┬─────────────┐
                   ▼          ▼          ▼             ▼
            ┌─────────┐  ┌────────┐  ┌────────┐  ┌──────────┐
            │ Gemini  │→ │ChatGPT │→ │Claude  │  │Synthesis │
            │ Agent   │  │ Agent  │  │ Agent  │  │ Engine   │
            │(Info)   │  │(Analysis)│ │(Exec)  │  │(Claude)  │
            └─────────┘  └────────┘  └────────┘  └──────────┘
                   │          │          │             │
                   └──────────┴──────────┴─────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │  Notion Results DB       │
                   │  - Original question     │
                   │  - Individual responses  │
                   │  - Synthesized analysis  │
                   │  - Metadata              │
                   └──────────────────────────┘
```

## Component Specifications

### 1. AI Agent Plugin System

**Base Interface:**
```python
class AIAgent(ABC):
    @abstractmethod
    async def query(self, question: str, context: Optional[Dict]) -> AgentResponse

    @abstractmethod
    async def health_check() -> bool
```

**Agents:**

1. **Gemini Agent** (Information Gathering)
   - Role: Research and data collection
   - Model: `gemini-pro`
   - Focus: Facts, statistics, trends, sources
   - Output: Structured research with citations

2. **ChatGPT Agent** (Strategic Analysis)
   - Role: Analysis and strategy development
   - Model: `gpt-4`
   - Input: Receives Gemini's research
   - Focus: Insights, SWOT, opportunities, strategies
   - Output: Strategic recommendations

3. **Claude Agent** (Execution Planning)
   - Role: Implementation and validation
   - Model: `claude-sonnet-4-5-20250929`
   - Input: Receives Gemini + ChatGPT results
   - Focus: Action plans, legal review, risk management
   - Output: Execution roadmap with validation

**Sequential Context Building:**
```
Gemini (research) → ChatGPT (analysis + gemini_result)
                  → Claude (execution + gemini_result + chatgpt_result)
```

### 2. Orchestrator

**Responsibilities:**
- Initialize all AI agent plugins
- Dispatch questions with context
- Execute sequential pipeline (Gemini → ChatGPT → Claude)
- Aggregate responses
- Trigger synthesis
- Handle partial failures gracefully

**Error Handling:**
- Minimum 1 successful agent required
- Failed agents return error responses
- Metadata tracks success rate
- Fallback synthesis if synthesis engine fails

### 3. Synthesis Engine

**Implementation:**
- Uses Claude (same as Claude Agent but different role)
- Receives all 3 agent responses
- Analyzes consensus and conflicts
- Resolves disagreements with reasoning
- Produces unified recommendation

**Fallback Strategy:**
- If synthesis fails, concatenate individual responses
- Mark as degraded mode in metadata

### 4. Notion Integration

**Inbox Database Schema:**
```
- 제목 (Title): Question text
- 상태 (Status): pending | processing | completed | failed
- 우선순위 (Priority): high | medium | low
- 카테고리 (Category): Select (optional)
- 결과링크 (Result Link): URL to result page
- Created Time
```

**Results Database Schema:**
```
- 제목 (Title): Question (truncated to 100 chars)
- 카테고리 (Category): From original question
- 처리시간 (Processing Time): Number (seconds)
- 성공 에이전트 (Successful Agents): Number
- 완료시각 (Completed At): Date
```

**Notion Client Responsibilities:**
- Query pending questions (filtered, sorted)
- Update question status
- Create result pages with rich formatting
- Link results back to inbox
- Rate limiting (3 req/sec)

### 5. Notion Watcher

**Behavior:**
- Polls Inbox DB every 30-60 seconds
- Maintains `processing_ids` set (active)
- Maintains `processed_ids` set (completed)
- Prevents duplicate processing
- Semaphore limits concurrent tasks (default: 5)

**Lifecycle:**
1. Query `status=pending` questions
2. Filter out already processing/processed
3. Update status: `pending` → `processing`
4. Call orchestrator callback
5. On success: create result page, link, mark `completed`
6. On failure: mark `failed`

## Data Flow

### Processing Pipeline

```
1. INPUT (Notion Inbox)
   User creates page with question
   Status: pending
   ↓

2. DETECTION (Watcher polls)
   Find pending questions
   Filter duplicates
   Update status → processing
   ↓

3. ORCHESTRATION (Sequential AI execution)
   a) Gemini: Information gathering
   b) ChatGPT: Analysis (+ Gemini context)
   c) Claude: Execution (+ Gemini + ChatGPT context)
   ↓

4. SYNTHESIS (Claude synthesis engine)
   Analyze 3 responses
   Resolve conflicts
   Generate unified recommendation
   ↓

5. OUTPUT (Notion Results DB)
   Create formatted result page:
   - Original question
   - Individual responses (toggles)
   - Synthesized analysis (main content)
   - Metadata
   ↓

6. COMPLETION (Update Inbox)
   Link result page
   Update status → completed
   Timestamp
```

### Data Models

**Question:**
```python
@dataclass
class Question:
    page_id: str
    text: str
    status: QuestionStatus
    priority: QuestionPriority
    category: Optional[str]
    created_at: datetime
    metadata: Optional[dict]
```

**AgentResponse:**
```python
@dataclass
class AgentResponse:
    agent_name: str          # "gemini" | "chatgpt" | "claude"
    content: str             # Response text
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] # tokens, duration, model
    error: Optional[str]
```

## Error Handling & Resilience

### 1. Retry Logic (Exponential Backoff)

```python
@async_retry(max_attempts=3, delay=1.0, backoff=2.0)
async def query(...):
    # API call
```

- **Max attempts:** 3
- **Initial delay:** 1-2 seconds
- **Backoff:** Exponential (2x)
- **Applied to:** All external API calls

### 2. Rate Limiting (Token Bucket)

Per-service rate limits:
- **Gemini:** 60 requests/minute
- **OpenAI:** 50 requests/minute
- **Anthropic:** 50 requests/minute
- **Notion:** 3 requests/second

Implementation:
- Async token bucket with semaphore
- Automatic queueing when limit reached
- Per-service tracking

### 3. Circuit Breaker

Configuration:
- **Failure threshold:** 5 consecutive failures
- **Recovery timeout:** 60 seconds
- **States:** CLOSED → OPEN → HALF_OPEN

Behavior:
- Tracks failures per agent
- Opens circuit after threshold
- Prevents cascading failures
- Auto-recovery after timeout

### 4. Partial Failure Handling

**Orchestrator Strategy:**
- Continue if ≥1 agent succeeds
- Include error responses in output
- Track success rate in metadata
- Synthesis adapts to missing responses

**Example:**
```
Gemini: ❌ Failed (API error)
ChatGPT: ✅ Success
Claude: ✅ Success
→ Proceed with 2/3 responses
→ Synthesis notes missing Gemini data
```

### 5. Graceful Degradation

**Synthesis Failure:**
- Fall back to concatenated responses
- Mark as "degraded mode" in metadata
- Still deliver value to user

**Notion Failure:**
- Log error with full context
- Mark question as `failed`
- Retry on next poll cycle

## Configuration Management

### Structure

```yaml
# config.yaml

system:
  polling_interval: 30
  max_concurrent_tasks: 5
  log_level: INFO
  environment: production

agents:
  gemini:
    model: gemini-pro
    timeout: 120
    max_retries: 3
  chatgpt:
    model: gpt-4
    timeout: 120
    temperature: 0.7
  claude:
    model: claude-sonnet-4-5-20250929
    timeout: 120

rate_limits:
  notion: {max_requests: 3, time_window: 1}
  gemini: {max_requests: 60, time_window: 60}
  # ...

circuit_breakers:
  failure_threshold: 5
  recovery_timeout: 60
```

### Environment Variables (.env)

```bash
# API Keys (secrets)
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
GEMINI_API_KEY=xxx
NOTION_API_KEY=secret_xxx

# Notion Database IDs
NOTION_INBOX_DB_ID=xxx
NOTION_RESULTS_DB_ID=xxx

# System (optional overrides)
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Security:**
- API keys: Environment variables only
- `.env` file: Git-ignored
- `.env.example`: Template committed to repo
- No secrets in YAML config

## Deployment

### Local Development

```bash
# 1. Setup
./scripts/setup.sh

# 2. Configure .env
cp .env.example .env
# Edit .env with API keys

# 3. Run
python main.py
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Considerations

1. **Logging:**
   - Rotating file handler (10MB, 5 backups)
   - Structured logging with timestamps
   - Error tracking with stack traces

2. **Monitoring:**
   - Health check endpoint (all services)
   - Processing metrics (duration, success rate)
   - Error rate monitoring

3. **Scaling:**
   - Horizontal: Multiple instances (different Inbox DBs)
   - Vertical: Increase `max_concurrent_tasks`
   - Rate limits prevent API overload

## Testing Strategy

### Unit Tests

**Coverage Areas:**
- Agent interface implementations
- Orchestrator logic (mocked agents)
- Synthesis engine (mocked Claude)
- Notion client (mocked API)
- Error handling (retry, circuit breaker)

**Example:**
```python
@pytest.mark.asyncio
async def test_partial_agent_failure():
    # Test orchestrator continues with 2/3 agents
    assert result['metadata']['successful_agents'] == 2
```

### Integration Tests

- End-to-end question processing
- Notion API interactions (test database)
- Real AI agent calls (rate-limited)

### Manual Testing

- Create test questions in Notion Inbox
- Verify result page formatting
- Check error handling (invalid API keys)

## Future Enhancements

**Phase 2 Considerations:**

1. **Caching:** Cache similar questions to reduce API costs
2. **Webhooks:** Real-time Notion integration (vs polling)
3. **UI Dashboard:** Web interface for monitoring
4. **Agent Marketplace:** Pluggable agent system
5. **Multi-language:** Support non-English questions
6. **Streaming:** Stream responses to Notion in real-time
7. **Analytics:** Usage tracking, cost analysis

## Appendix

### Project Structure

```
universal-ai-orchestrator/
├── .env.example
├── .env (git-ignored)
├── .gitignore
├── README.md
├── requirements.txt
├── config.yaml
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── prompts.py
│   └── security.py
│
├── core/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── synthesis_engine.py
│   └── notion_watcher.py
│
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── gemini_agent.py
│   ├── chatgpt_agent.py
│   └── claude_agent.py
│
├── integrations/
│   ├── __init__.py
│   └── notion_client.py
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── retry.py
│   └── rate_limiter.py
│
├── models/
│   ├── __init__.py
│   ├── agent_response.py
│   └── question.py
│
├── tests/
│   ├── __init__.py
│   ├── test_orchestrator.py
│   ├── test_agents.py
│   └── test_notion.py
│
├── docs/
│   └── plans/
│       └── 2025-11-09-ai-orchestrator-design.md
│
├── scripts/
│   ├── setup.sh
│   └── run.sh
│
└── main.py
```

### Dependencies

**Core:**
- python-dotenv (config)
- pyyaml (config)
- asyncio (async execution)

**AI SDKs:**
- anthropic (Claude)
- openai (ChatGPT)
- google-generativeai (Gemini)

**Integrations:**
- notion-client (Notion API)

**Utilities:**
- aiohttp (async HTTP)
- tenacity (retry logic)

### Glossary

- **Orchestrator:** Central coordinator managing AI agents
- **Agent:** Plugin implementing AIAgent interface
- **Synthesis:** Process of merging multiple AI responses
- **Watcher:** Service monitoring Notion Inbox for new questions
- **Circuit Breaker:** Pattern preventing cascade failures
- **Rate Limiter:** Token bucket controlling API request rate

---

**Document Approval:**
- Design validated through brainstorming process
- All requirements captured
- Ready for implementation

**Next Steps:**
1. Set up project directory structure
2. Create implementation plan
3. Begin development with TDD approach
