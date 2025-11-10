"""
Anthropic Claude Agent implementation
"""

import anthropic
from datetime import datetime
from typing import Optional, Dict
from .base import AIAgent
from models.agent_response import AgentResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeAgent(AIAgent):
    """
    Anthropic Claude 실행 계획 에이전트
    """

    def __init__(self, api_key: str, config: Dict):
        super().__init__(api_key, config)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = config.get('model', 'claude-sonnet-4-5-20250929')

    async def query(self, question: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        실행 계획 수립 및 검증
        """
        start_time = datetime.now()

        try:
            # 이전 두 에이전트 결과 활용
            gemini_result = context.get('gemini_result', '') if context else ''
            chatgpt_result = context.get('chatgpt_result', '') if context else ''

            prompt = self._build_prompt(question, gemini_result, chatgpt_result, context)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = message.content[0].text

            return AgentResponse(
                agent_name=self.name,
                content=content,
                metadata={
                    'tokens': message.usage.input_tokens + message.usage.output_tokens,
                    'duration': (datetime.now() - start_time).total_seconds(),
                    'model': self.model
                },
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Claude 오류: {e}", exc_info=True)
            return AgentResponse(
                agent_name=self.name,
                content="",
                metadata={},
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )

    def _build_prompt(self, question: str, research: str,
                     analysis: str, context: Optional[Dict]) -> str:
        """프롬프트 생성"""
        category = context.get('category', '일반') if context else '일반'

        prompt = f"""
당신은 {category} 분야의 실행 전문가이자 검증자입니다.

질문: {question}

정보 수집 결과 (Gemini):
{research}

분석 및 전략 (ChatGPT):
{analysis}

당신의 역할:
1. **실행 계획**: 단계별 액션 플랜 (타임라인 포함)
2. **법적/규제 검토**: 준수 사항 및 리스크
3. **리소스 계획**: 필요한 예산, 인력, 도구
4. **리스크 관리**: 시나리오별 대응 방안
5. **검증**: 앞선 분석의 논리적 오류나 누락 지적
6. **최종 권고**: 실행 여부 및 이유

**비판적이고 현실적으로 검토하세요.**
**법적 리스크를 명확히 지적하세요.**

출력 구조:
# Executive Summary
# 실행 계획
# 법적/규제 검토
# 리스크 관리
# Next Actions (우선순위별)
# 최종 의사결정 권고
"""
        return prompt.strip()

    async def health_check(self) -> bool:
        """API 연결 확인"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return bool(message.content)
        except:
            return False
