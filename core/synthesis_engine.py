"""
Synthesis Engine for merging AI responses
"""

import anthropic
from typing import List
from models.agent_response import AgentResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class SynthesisEngine:
    """
    3개 AI 응답을 통합하여 지능형 합의 생성
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    async def synthesize(self, question: str, responses: List[AgentResponse]) -> str:
        """
        3개 응답을 통합

        Args:
            question: 원본 질문
            responses: [gemini_response, chatgpt_response, claude_response]

        Returns:
            통합된 최종 분석
        """

        # 응답 정리
        gemini = next((r for r in responses if r.agent_name == "gemini"), None)
        chatgpt = next((r for r in responses if r.agent_name == "chatgpt"), None)
        claude = next((r for r in responses if r.agent_name == "claude"), None)

        if not all([gemini, chatgpt, claude]):
            logger.warning("일부 에이전트 응답 누락")

        prompt = self._build_synthesis_prompt(
            question,
            gemini.content if gemini and gemini.success else "정보 없음",
            chatgpt.content if chatgpt and chatgpt.success else "분석 없음",
            claude.content if claude and claude.success else "계획 없음",
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=5000,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"통합 엔진 오류: {e}", exc_info=True)
            raise

    def _build_synthesis_prompt(
        self,
        question: str,
        gemini_content: str,
        chatgpt_content: str,
        claude_content: str,
    ) -> str:
        """통합 프롬프트 생성"""

        prompt = f"""
당신은 최고의 비즈니스 의사결정 컨설턴트입니다.

3명의 전문가가 다음 질문에 대해 각자의 관점에서 답변했습니다:

**질문:** {question}

---

**전문가 1 (정보 수집):**
{gemini_content}

---

**전문가 2 (전략 분석):**
{chatgpt_content}

---

**전문가 3 (실행 계획):**
{claude_content}

---

당신의 임무:
1. 3명의 의견을 **종합**하여 하나의 일관된 분석 생성
2. 의견이 일치하는 부분과 **상충하는 부분** 명확히 구분
3. 상충시 **가장 타당한 의견** 선택하고 이유 설명
4. 누락된 중요 사항이 있다면 **보완**
5. 최종적으로 **실행 가능한 단일 권고안** 제시

**출력 구조:**
# 종합 분석
## 핵심 발견사항 (3-5개)
## 전문가 의견 일치 영역
## 의견 상충 및 해결
## 보완 사항
## 최종 권고사항
## Next Steps (우선순위별)

**명확하고 실행 가능하게 작성하세요.**
"""
        return prompt.strip()
