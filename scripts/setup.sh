#!/bin/bash

echo "🚀 Universal AI Orchestrator 설치 시작"

# 1. Python 가상환경 생성
echo "📦 가상환경 생성 중..."
python3 -m venv venv
source venv/bin/activate

# 2. 의존성 설치
echo "📚 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. 디렉토리 확인
echo "📁 디렉토리 확인 중..."
mkdir -p logs

# 4. .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다"
    echo "📝 .env.example을 복사하여 .env를 생성하세요"
    cp .env.example .env
    echo "✅ .env 파일 생성 완료 - API 키를 입력하세요"
else
    echo "✅ .env 파일 존재"
fi

# 5. 설정 검증
echo "🔍 설정 검증 중..."
python -c "from config.settings import ConfigManager; ConfigManager()" && echo "✅ 설정 유효" || echo "❌ 설정 오류 - .env 파일을 확인하세요"

echo ""
echo "🎉 설치 완료!"
echo ""
echo "다음 단계:"
echo "1. .env 파일에 API 키 입력"
echo "2. python main.py 실행"
