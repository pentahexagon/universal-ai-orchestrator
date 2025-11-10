# Universal AI Orchestrator

다중 AI 에이전트 통합 시스템으로 Gemini, ChatGPT, Claude의 응답을 종합하여 지능형 합의를 도출하고 Notion 워크플로우를 자동화합니다.

## 🎯 주요 기능

- **다중 AI 통합**: Gemini (정보수집) → ChatGPT (전략분석) → Claude (실행계획)
- **AI 기반 합성**: Claude를 사용한 지능형 응답 통합
- **Notion 워크플로우**: Inbox 데이터베이스 자동 모니터링 및 결과 생성
- **강력한 에러 처리**: Retry 로직, Rate limiting, Circuit breaker
- **비동기 처리**: 빠른 응답 시간과 높은 처리량

## 📋 요구사항

- Python 3.11+
- Notion 계정 및 Integration
- API 키:
  - Anthropic Claude
  - OpenAI GPT-4
  - Google Gemini

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론 (또는 다운로드)
cd universal-ai-orchestrator

# 설치 스크립트 실행
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. 환경 설정

`.env` 파일을 열고 API 키를 입력하세요:

```bash
# AI API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-gemini-key-here

# Notion Configuration
NOTION_API_KEY=secret_your-notion-integration-token
NOTION_INBOX_DB_ID=your-inbox-database-id
NOTION_RESULTS_DB_ID=your-results-database-id
```

### 3. Notion 데이터베이스 설정

**Inbox 데이터베이스 생성:**

| 속성 이름 | 타입 | 설명 |
|---------|------|------|
| 제목 | Title | 질문 내용 |
| 상태 | Status | pending, processing, completed, failed |
| 우선순위 | Select | high, medium, low |
| 카테고리 | Select | (선택사항) |
| 결과링크 | URL | 결과 페이지 링크 (자동 입력) |

**Results 데이터베이스 생성:**

| 속성 이름 | 타입 | 설명 |
|---------|------|------|
| 제목 | Title | 질문 (자동 입력) |
| 카테고리 | Select | (자동 입력) |
| 처리시간 | Number | 초 단위 (자동 입력) |
| 성공 에이전트 | Number | 성공한 AI 수 (자동 입력) |

### 4. 실행

```bash
source venv/bin/activate
python main.py
```

## 📖 사용 방법

1. **Notion Inbox에 질문 추가**
   - 새 페이지 생성
   - 제목에 질문 입력
   - 상태를 "pending"으로 설정

2. **자동 처리 대기**
   - Orchestrator가 30초마다 체크
   - 3개 AI 에이전트가 순차적으로 분석
   - Results DB에 통합 결과 생성

3. **결과 확인**
   - Inbox 페이지의 "결과링크"에서 확인
   - 통합 분석 + 개별 AI 응답 모두 확인 가능

## 🏗️ 아키텍처

```
Notion Inbox (pending)
    ↓ (30초 폴링)
Watcher 감지
    ↓
Orchestrator 실행
    ├─ Gemini (정보수집)
    ├─ ChatGPT (분석) ← Gemini 결과
    └─ Claude (실행) ← Gemini + ChatGPT 결과
    ↓
Synthesis Engine (Claude)
    ↓
Notion Results 생성
    ↓
Inbox 상태 업데이트 (completed)
```

## 🔧 설정

`config.yaml`에서 시스템 설정을 변경할 수 있습니다:

```yaml
system:
  polling_interval: 30        # 폴링 간격 (초)
  max_concurrent_tasks: 5     # 동시 처리 수

agents:
  gemini:
    model: gemini-pro
  chatgpt:
    model: gpt-4
  claude:
    model: claude-sonnet-4-5-20250929
```

## 📁 프로젝트 구조

```
universal-ai-orchestrator/
├── config/          # 설정 관리
├── core/            # Orchestrator, Watcher, Synthesis
├── agents/          # AI 에이전트 플러그인
├── integrations/    # Notion 클라이언트
├── models/          # 데이터 모델
├── utils/           # 유틸리티 (logging, retry, rate limiting)
├── docs/            # 설계 문서
├── scripts/         # 설치/실행 스크립트
├── main.py          # 실행 진입점
└── config.yaml      # 시스템 설정
```

## 🔍 로깅

로그는 다음 위치에 저장됩니다:
- **콘솔**: 실시간 로그
- **파일**: `logs/orchestrator.log` (10MB씩 5개 파일 로테이션)

## ⚡ 성능 및 제한

- **Rate Limiting**:
  - Gemini: 60 req/min
  - OpenAI: 50 req/min
  - Anthropic: 50 req/min
  - Notion: 3 req/sec

- **Retry 로직**: 실패시 3회 자동 재시도 (exponential backoff)
- **Circuit Breaker**: 5회 연속 실패시 60초간 일시 중단

## 🧪 개발

### 테스트 실행

```bash
pytest tests/
```

### 코드 포맷팅

```bash
black .
ruff check .
```

## 🔧 유틸리티 스크립트

### AI 응답 집계 도구

여러 AI 에이전트의 응답을 분석하고 합의를 도출하는 스크립트:

```bash
# JSONL 파일에서 AI 응답 로드 및 합의 도출
python scripts/aggregate_fallback.py data/ai_responses.jsonl out/consensus_fallback.jsonl
```

**기능:**
- 질문별로 응답 그룹화
- 성공한 응답만 필터링
- 가장 상세한 응답 선택
- 통계 정보 생성 (성공률, 에이전트 분포, 평균 길이)

**입력 형식 (JSONL):**
```json
{"question_id": "q1", "question": "What is AI?", "agent_name": "gemini", "success": true, "content": "..."}
{"question_id": "q1", "question": "What is AI?", "agent_name": "chatgpt", "success": true, "content": "..."}
```

**출력 형식 (JSONL):**
```json
{
  "question_id": "q1",
  "question": "What is AI?",
  "consensus": {
    "success": true,
    "content": "...",
    "selected_agent": "chatgpt",
    "total_responses": 3,
    "successful_responses": 3,
    "failed_responses": 0
  }
}
```

### 시크릿 관리 도구

API 키를 안전하게 관리하는 스크립트들:

```bash
# .env 파일 생성
bash scripts/save_local_env.sh

# OS 키링에 저장
pip install keyring
python scripts/save_keyring.py

# GitHub Secrets에 등록
bash scripts/push_github_secrets.sh
```

자세한 내용은 [시크릿 관리 가이드](docs/SECRETS_MANAGEMENT.md)를 참고하세요.

## 📚 문서

- [설계 문서](docs/plans/2025-11-09-ai-orchestrator-design.md)

## 🛠️ 트러블슈팅

**Q: "설정 검증 실패" 오류**
A: `.env` 파일에 모든 API 키가 올바르게 입력되었는지 확인하세요.

**Q: Notion 연결 실패**
A:
- Integration이 두 데이터베이스에 모두 연결되었는지 확인
- 데이터베이스 ID가 올바른지 확인

**Q: AI 에이전트 실패**
A:
- API 키가 유효한지 확인
- Rate limit을 초과하지 않았는지 확인
- 로그에서 자세한 에러 메시지 확인

## 📝 라이선스

MIT License

## 🤝 기여

Issue 및 Pull Request를 환영합니다!

---

**Made with ❤️ using Claude Code**
