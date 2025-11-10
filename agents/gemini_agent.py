"""
Google Gemini Agent implementation
"""

import google.generativeai as genai
from datetime import datetime
from typing import Optional, Dict
from .base import AIAgent
from models.agent_response import AgentResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class GeminiAgent(AIAgent):
    """
    Google Gemini 정보 수집 에이전트
    """

    def __init__(self, api_key: str, config: Dict):
        super().__init__(api_key, config)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.get('model', 'gemini-pro'))

    async def query(self, question: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        정보 수집 수행
        """
        start_time = datetime.now()

        try:
            # 역할별 프롬프트 구성
            prompt = self._build_prompt(question, context)

            # Gemini 호출
            response = self.model.generate_content(prompt)

            # 응답 구성
            return AgentResponse(
                agent_name=self.name,
                content=response.text,
                metadata={
                    'tokens': len(response.text.split()),
                    'duration': (datetime.now() - start_time).total_seconds()
                },
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini 오류: {e}", exc_info=True)
            return AgentResponse(
                agent_name=self.name,
                content="",
                metadata={},
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )

    def _build_prompt(self, question: str, context: Optional[Dict]) -> str:
        """프롬프트 생성"""
        category = context.get('category', '일반') if context else '일반'

        base_prompt = f"""
당신은 {category} 분야의 정보 수집 전문가입니다.

질문: {question}

다음 정보를 웹에서 찾아 정리하세요:
1. 관련 데이터 및 통계 (최신 정보)
2. 시장 트렌드
3. 주요 사례 또는 비교 대상
4. 규제 및 법적 고려사항
5. 전문가 의견 또는 리뷰

**출처 URL을 반드시 포함하세요.**
**구조화된 형식으로 정리하세요.**
"""
        return base_prompt.strip()

    async def health_check(self) -> bool:
        """API 연결 확인"""
        try:
            test_response = self.model.generate_content("Hello")
            return bool(test_response.text)
        except:
            return False
