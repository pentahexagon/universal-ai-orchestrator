"""
OpenAI ChatGPT Agent implementation
"""

from openai import AsyncOpenAI
from datetime import datetime
from typing import Optional, Dict
from .base import AIAgent
from models.agent_response import AgentResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class ChatGPTAgent(AIAgent):
    """
    OpenAI ChatGPT 분석 에이전트
    """

    def __init__(self, api_key: str, config: Dict):
        super().__init__(api_key, config)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get("model", "gpt-4")
        self.temperature = config.get("temperature", 0.7)

    async def query(
        self, question: str, context: Optional[Dict] = None
    ) -> AgentResponse:
        """
        분석 및 전략 수립
        """
        start_time = datetime.now()

        try:
            # 이전 에이전트 결과 (Gemini)가 있으면 활용
            gemini_result = context.get("gemini_result", "") if context else ""

            prompt = self._build_prompt(question, gemini_result, context)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 전략 분석 전문가입니다."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
            )

            content = response.choices[0].message.content

            return AgentResponse(
                agent_name=self.name,
                content=content,
                metadata={
                    "tokens": response.usage.total_tokens,
                    "duration": (datetime.now() - start_time).total_seconds(),
                    "model": self.model,
                },
                timestamp=datetime.now(),
                success=True,
            )

        except Exception as e:
            logger.error(f"ChatGPT 오류: {e}", exc_info=True)
            return AgentResponse(
                agent_name=self.name,
                content="",
                metadata={},
                timestamp=datetime.now(),
                success=False,
                error=str(e),
            )

    def _build_prompt(
        self, question: str, research: str, context: Optional[Dict]
    ) -> str:
        """프롬프트 생성"""
        category = context.get("category", "일반") if context else "일반"

        prompt = f"""
당신은 {category} 분야의 전략 분석가입니다.

질문: {question}

수집된 정보:
{research}

다음을 분석하세요:
1. 핵심 인사이트 (3-5개)
2. SWOT 분석
3. 기회와 위험 요인
4. 전략적 제안 (구체적이고 실행 가능한)
5. 예상 결과 및 지표

**창의적이고 데이터 기반으로 분석하세요.**
"""
        return prompt.strip()

    async def health_check(self) -> bool:
        """API 연결 확인"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return bool(response.choices)
        except Exception:
            return False
