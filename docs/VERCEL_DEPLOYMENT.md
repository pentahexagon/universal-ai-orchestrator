# Vercel 배포 가이드

Universal AI Orchestrator를 Vercel에 배포하고 도메인을 연결하는 방법을 설명합니다.

## 🚀 빠른 배포

### 1. Vercel CLI 설치 (선택사항)

```bash
npm install -g vercel
```

### 2. Vercel에 로그인

```bash
vercel login
```

### 3. 프로젝트 배포

```bash
cd frontend
vercel
```

## 🌐 웹 UI로 배포 (권장)

### 1. Vercel 대시보드 접속

https://vercel.com/dashboard 로 이동하여 로그인

### 2. 새 프로젝트 import

1. "Add New" → "Project" 클릭
2. GitHub repository 연결
   - `pentahexagon/universal-ai-orchestrator` 선택
3. 프로젝트 설정:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js (자동 감지됨)
   - **Build Command**: `npm run build` (기본값)
   - **Output Directory**: `.next` (기본값)

### 3. 환경 변수 설정

Environment Variables 섹션에서 다음 변수 추가:

```
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GEMINI_API_KEY=your-gemini-key
```

**중요**:
- 이 키들은 Vercel Serverless Functions에서만 사용됩니다
- 브라우저에 노출되지 않습니다
- `NEXT_PUBLIC_` 접두사는 붙이지 마세요

### 4. 배포 시작

"Deploy" 버튼 클릭

배포 완료 후 자동으로 URL 생성: `https://your-project.vercel.app`

## 🔗 커스텀 도메인 연결

Vercel에서 구매한 도메인을 연결하는 방법:

### 1. 도메인 추가

1. Vercel 프로젝트 → "Settings" → "Domains"
2. 구매한 도메인 입력 (예: `my-ai-chat.com`)
3. "Add" 클릭

### 2. DNS 설정 (Vercel에서 구매한 경우)

자동으로 DNS가 설정됩니다. 수동 설정이 필요한 경우:

**A 레코드:**
```
Type: A
Name: @
Value: 76.76.21.21
```

**CNAME 레코드 (www):**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### 3. 검증 및 적용

- DNS 전파는 최대 48시간 소요 (보통 몇 분 내)
- Vercel이 자동으로 SSL 인증서 발급 (Let's Encrypt)
- `https://your-domain.com` 으로 접속 가능

## 🎯 배포 모드

### Development Mode (기본값)

- API 키 없이도 작동
- 시뮬레이션 응답 사용
- 로컬 개발 및 테스트용

### Production Mode

환경 변수에 API 키 설정 시 자동 활성화:
- 실제 AI API 호출
- Python orchestrator 사용
- 실시간 AI 응답

## 🔧 설정 파일

### vercel.json

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "outputDirectory": ".next",
  "env": {
    "OPENAI_API_KEY": "@openai_api_key",
    "ANTHROPIC_API_KEY": "@anthropic_api_key",
    "GEMINI_API_KEY": "@gemini_api_key"
  }
}
```

## 📊 모니터링

### Vercel Analytics

1. 프로젝트 → "Analytics" 탭
2. 방문자 수, 응답 시간, 에러율 확인

### Logs

1. 프로젝트 → "Deployments" → 최신 배포 클릭
2. "Runtime Logs" 에서 실시간 로그 확인
3. API 오류, 성능 이슈 디버깅

## 🔄 자동 배포

### GitHub Integration

1. main 브랜치에 push → 자동 배포
2. PR 생성 → Preview 배포 (고유 URL)
3. PR 병합 → Production 배포

### 배포 설정

프로젝트 Settings → Git:
- **Production Branch**: `main`
- **Automatically deploy branch**: ✅ 활성화
- **Preview deployments**: ✅ 활성화

## 🛠️ 트러블슈팅

### 배포 실패

**문제**: Build fails with module errors
**해결**:
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

### API 오류

**문제**: "AI 처리 중 오류" 메시지
**해결**:
1. Vercel 환경 변수 확인
2. API 키 유효성 검증
3. Runtime Logs 확인

### 도메인 연결 실패

**문제**: 도메인이 연결되지 않음
**해결**:
1. DNS 전파 확인: https://dnschecker.org
2. Vercel DNS 설정 확인
3. 48시간 대기

## 📱 모바일 최적화

Tailwind CSS가 자동으로 반응형 디자인 제공:
- 모바일: 한 칼럼 레이아웃
- 태블릿: 적응형 레이아웃
- 데스크톱: 최대 너비 제한

## 🔐 보안

- ✅ HTTPS 자동 적용 (SSL/TLS)
- ✅ 환경 변수 암호화
- ✅ API 키 브라우저 노출 방지
- ✅ CORS 자동 설정

## 💰 비용

### Vercel Hobby Plan (무료)

- 무제한 배포
- 100GB 대역폭/월
- Serverless Functions: 100GB-Hrs

### Vercel Pro ($20/월)

- 더 많은 대역폭
- Advanced analytics
- 팀 협업 기능

## 📚 추가 자료

- [Vercel 공식 문서](https://vercel.com/docs)
- [Next.js 배포 가이드](https://nextjs.org/docs/deployment)
- [커스텀 도메인 설정](https://vercel.com/docs/concepts/projects/domains)
