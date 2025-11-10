# Secrets Management Guide

안전하게 API 키와 시크릿을 관리하는 방법을 설명합니다.

## 🔐 보안 원칙

- ❌ **절대로** API 키를 코드에 하드코딩하지 마세요
- ❌ **절대로** `.env` 파일을 Git에 커밋하지 마세요
- ✅ 로컬에서는 `.env` 파일 또는 OS 키링 사용
- ✅ CI/CD에서는 GitHub Secrets 사용

## 📋 로컬 개발 환경

### 방법 1: `.env` 파일 사용 (권장)

```bash
# 대화형 스크립트로 .env 파일 생성
bash scripts/save_local_env.sh
```

이 스크립트는:
- 대화형으로 API 키 입력받기
- `.env` 파일 생성 (권한 600으로 보안 강화)
- `.gitignore`에 이미 등록되어 있어 Git에 커밋되지 않음

### 방법 2: OS 키링 사용 (macOS/Windows/Linux)

```bash
# keyring 패키지 설치
pip install keyring

# 대화형 스크립트로 키링에 저장
python scripts/save_keyring.py
```

OS 키링의 장점:
- 파일로 저장되지 않아 더 안전
- OS 레벨 암호화
- 시스템 재부팅 후에도 유지

### 시크릿 우선순위

`config/settings.py`는 다음 순서로 시크릿을 찾습니다:

1. **환경변수** (최우선)
2. **OS 키링** (keyring 설치 시)
3. **None** (찾지 못하면 검증 오류)

## 🔧 CI/CD 환경

### GitHub Actions에 시크릿 등록

#### 옵션 1: GitHub CLI 사용 (권장)

```bash
# gh CLI 로그인
gh auth login

# 대화형 스크립트로 GitHub Secrets 등록
bash scripts/push_github_secrets.sh
```

#### 옵션 2: 웹 UI 사용

1. GitHub 리포지토리 → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. 다음 시크릿 추가:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`
   - `NOTION_API_KEY`
   - `NOTION_DATABASE_ID`

### CI 워크플로우에서 사용

`.github/workflows/ci.yml`에서 자동으로 환경변수로 주입됩니다:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  # ...
```

## 📝 필요한 시크릿 목록

| 키 이름 | 설명 | 필수 여부 |
|---------|------|-----------|
| `OPENAI_API_KEY` | OpenAI API 키 (ChatGPT) | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic API 키 (Claude) | ✅ |
| `GEMINI_API_KEY` | Google Gemini API 키 | ✅ |
| `NOTION_API_KEY` | Notion Integration Token | ✅ |
| `NOTION_INBOX_DB_ID` | Notion Inbox 데이터베이스 ID | ✅ |
| `NOTION_RESULTS_DB_ID` | Notion Results 데이터베이스 ID | ✅ |

## 🛡️ 보안 주의사항

### Fork에서의 Secrets

- Fork된 리포지토리의 PR에서는 **secrets가 자동으로 노출되지 않습니다**
- 외부 기여자의 PR에서 secrets가 필요한 테스트는 실패할 수 있습니다
- Maintainer가 PR을 리뷰 후 수동으로 실행해야 합니다

### 파일 권한

```bash
# .env 파일은 소유자만 읽기/쓰기 가능하도록 설정
chmod 600 .env

# 확인
ls -la .env
# 출력: -rw------- 1 user group ... .env
```

## 🧪 테스트 환경

테스트 시 실제 API 키가 필요 없는 경우:

```python
# 환경변수를 mock으로 설정
import os
os.environ["OPENAI_API_KEY"] = "test-key"
```

또는 pytest fixture 사용:

```python
@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
```

## 📚 추가 자료

- [GitHub Secrets 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Python keyring 문서](https://github.com/jaraco/keyring)
- [dotenv 문서](https://github.com/theskumar/python-dotenv)
