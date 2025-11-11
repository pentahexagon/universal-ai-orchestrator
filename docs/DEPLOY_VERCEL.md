# Vercel 배포 가이드

이 문서는 Universal AI Orchestrator를 Vercel에 배포하는 방법을 설명합니다.

## 📋 필수 조건

- Vercel 계정
- GitHub 저장소와 연결된 Vercel 프로젝트
- 필요한 API 키들 (Anthropic, OpenAI, Gemini, Notion)

## 🔐 필수 비밀 값 설정

Vercel 프로젝트를 배포하려면 다음 세 가지 비밀 값이 필요합니다:

### GitHub Actions Secrets 설정

GitHub 저장소의 [**Settings → Secrets and variables → Actions**](../../settings/secrets/actions) 메뉴에서 다음 secrets을 추가하세요:

> 💡 **바로가기**: [GitHub Secrets 페이지로 이동](../../settings/secrets/actions)

1. **`VERCEL_TOKEN`** - Vercel Personal Access Token
   - Vercel 대시보드에서 생성: [Settings → Tokens](https://vercel.com/account/tokens)
   - "Create Token" 버튼 클릭
   - 토큰 이름 입력 후 생성
   - 생성된 토큰을 복사하여 GitHub Secret에 추가

2. **`VERCEL_ORG_ID`** - Vercel 조직 ID
   - Vercel 프로젝트 Settings → General 페이지에서 확인
   - 또는 Vercel CLI로 확인: `vercel project ls`

3. **`VERCEL_PROJECT_ID`** - 프로젝트 ID
   - Vercel 프로젝트 Settings → General 페이지에서 확인
   - 프로젝트를 생성한 후 자동으로 할당됨

### Vercel 대시보드에서 환경 변수 설정

Vercel 대시보드의 프로젝트 **Settings → Environment Variables**에서 다음 환경 변수를 추가하세요:

#### AI API Keys
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-gemini-key-here
```

#### Notion Configuration
```
NOTION_API_KEY=secret_your-notion-integration-token
NOTION_INBOX_DB_ID=your-inbox-database-id
NOTION_RESULTS_DB_ID=your-results-database-id
```

#### 시스템 설정 (선택사항)
```
LOG_LEVEL=INFO
POLLING_INTERVAL=30
MAX_CONCURRENT_TASKS=5
ENVIRONMENT=production
```

## 🚀 배포 방법

### 자동 배포 (GitHub Actions)

1. GitHub Secrets 설정 완료
2. `main` 브랜치에 푸시하면 자동으로 배포됩니다
3. GitHub Actions 탭에서 배포 진행 상황 확인

### 수동 배포 (Vercel CLI)

```bash
# Vercel CLI 설치
npm install -g vercel

# 로그인
vercel login

# 프로젝트 연결 (첫 배포시)
vercel link

# 배포
vercel --prod
```

## 📝 Vercel 프로젝트 생성

처음 배포하는 경우, Vercel에서 프로젝트를 먼저 생성해야 합니다:

1. [Vercel 대시보드](https://vercel.com/dashboard)에 로그인
2. "Add New..." → "Project" 클릭
3. GitHub 저장소 선택
4. 프로젝트 이름 입력
5. Framework Preset: "Other" 선택
6. 환경 변수 추가 (위의 목록 참조)
7. "Deploy" 클릭

프로젝트가 생성되면 Settings → General에서 `VERCEL_ORG_ID`와 `VERCEL_PROJECT_ID`를 확인할 수 있습니다.

## ⚠️ 중요 사항

### 배포 제한사항

이 프로젝트는 장기 실행 백그라운드 서비스입니다. Vercel의 Serverless Functions는 다음과 같은 제한이 있습니다:

- **실행 시간 제한**: 
  - Hobby: 10초
  - Pro: 60초
  - Enterprise: 900초 (15분)

- **폴링 서비스**: 현재 구조는 30초마다 Notion을 폴링하는 장기 실행 서비스입니다.

### 권장 배포 방법

이 프로젝트는 다음 플랫폼에 더 적합합니다:

1. **Railway**: 장기 실행 백그라운드 서비스 지원
2. **Render**: Background Workers 지원
3. **Fly.io**: 장기 실행 애플리케이션 지원
4. **AWS ECS/Fargate**: 컨테이너 기반 배포
5. **Google Cloud Run**: 컨테이너 배포 (최소 인스턴스 1개 설정)

### Vercel에서 실행하려면

Vercel에서 이 프로젝트를 실행하려면 아키텍처를 다음과 같이 수정해야 합니다:

1. **Cron Jobs 사용**: Vercel Cron으로 주기적 실행
2. **Webhook 방식**: Notion API webhook으로 실시간 처리
3. **API 엔드포인트**: 온디맨드 처리 방식으로 변경

## 🔍 배포 확인

배포가 완료되면:

1. Vercel 대시보드에서 배포 상태 확인
2. Deployment Logs에서 오류 확인
3. Runtime Logs에서 실행 로그 확인

## 🛠️ 문제 해결

### "Missing required environment variable"

→ Vercel 대시보드의 Environment Variables에서 모든 필수 환경 변수가 설정되어 있는지 확인

### "Build failed"

→ GitHub Actions 로그나 Vercel Build Logs에서 상세 오류 확인

### "Function execution timeout"

→ Vercel의 실행 시간 제한을 초과했습니다. 아키텍처 변경 필요

## 📚 관련 문서

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Vercel CLI](https://vercel.com/docs/cli)

## 💡 대안 배포 가이드

장기 실행 서비스 배포를 위한 대안 플랫폼 가이드는 별도 문서를 참조하세요:
- [Railway 배포 가이드](./DEPLOY_RAILWAY.md) (추천)
- [Render 배포 가이드](./DEPLOY_RENDER.md)
- [Docker 배포 가이드](./DEPLOY_DOCKER.md)
