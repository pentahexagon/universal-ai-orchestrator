"""
Central AI Orchestrator
"""

from typing import Dict, List
from datetime import datetime

from agents.base import AIAgent
from agents.gemini_agent import GeminiAgent
from agents.chatgpt_agent import ChatGPTAgent
from agents.claude_agent import ClaudeAgent
from models.agent_response import AgentResponse
from core.synthesis_engine import SynthesisEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """
    중앙 조율자 - 모든 AI 에이전트를 조율
    """

    def __init__(self, config: Dict):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config

        # AI 에이전트 초기화
        self.agents: List[AIAgent] = [
            GeminiAgent(
                api_key=config["api_keys"]["gemini"], config=config["agents"]["gemini"]
            ),
            ChatGPTAgent(
                api_key=config["api_keys"]["openai"], config=config["agents"]["chatgpt"]
            ),
            ClaudeAgent(
                api_key=config["api_keys"]["anthropic"],
                config=config["agents"]["claude"],
            ),
        ]

        # 통합 엔진
        self.synthesis = SynthesisEngine(api_key=config["api_keys"]["anthropic"])

    async def process_question(self, question: str, context: Dict = None) -> Dict:
        """
        질문 처리 메인 파이프라인

        Args:
            question: 사용자 질문
            context: 추가 컨텍스트

        Returns:
            {
                'success': bool,
                'question': str,
                'responses': {...},
                'synthesis': str,
                'metadata': {...}
            }
        """
        logger.info(f"📥 질문 수신: {question[:100]}...")
        start_time = datetime.now()
        errors = []

        try:
            # STEP 1: AI 에이전트 순차 실행
            logger.info("🔄 Step 1: AI 에이전트 순차 실행...")
            responses = await self._dispatch_sequential(question, context or {})

            # STEP 2: 응답 검증
            successful = [r for r in responses if r.success]
            if not successful:
                raise Exception("모든 AI 에이전트 실패")

            logger.info(f"✓ {len(successful)}/{len(responses)} 에이전트 성공")

            # STEP 3: 합성 (통합)
            logger.info("🔄 Step 2: 응답 통합 중...")
            try:
                synthesis = await self.synthesis.synthesize(question, responses)
            except Exception as e:
                logger.error(f"통합 실패: {e}")
                errors.append(f"synthesis: {str(e)}")
                synthesis = self._create_fallback_synthesis(responses)

            # STEP 4: 결과 패키징
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ 처리 완료 ({duration:.1f}초)")

            return {
                "success": True,
                "question": question,
                "responses": {
                    r.agent_name: {
                        "content": r.content,
                        "success": r.success,
                        "error": r.error,
                        "metadata": r.metadata,
                    }
                    for r in responses
                },
                "synthesis": synthesis,
                "metadata": {
                    "total_duration": duration,
                    "timestamp": datetime.now().isoformat(),
                    "successful_agents": len(successful),
                    "total_agents": len(responses),
                    "errors": errors,
                },
            }

        except Exception as e:
            logger.error(f"❌ 오케스트레이션 오류: {e}", exc_info=True)

            return {
                "success": False,
                "question": question,
                "error": str(e),
                "errors": errors,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "duration": (datetime.now() - start_time).total_seconds(),
                },
            }

    async def _dispatch_sequential(
        self, question: str, context: Dict
    ) -> List[AgentResponse]:
        """
        AI 에이전트를 순차적으로 호출 (각 AI가 이전 결과를 받음)
        Gemini → ChatGPT → Claude
        """
        responses = []

        try:
            # 1. Gemini (정보 수집)
            gemini_response = await self.agents[0].query(question, context)
            responses.append(gemini_response)

            # 2. ChatGPT (분석) - Gemini 결과 활용
            chatgpt_context = {
                **context,
                "gemini_result": (
                    gemini_response.content if gemini_response.success else ""
                ),
            }
            chatgpt_response = await self.agents[1].query(question, chatgpt_context)
            responses.append(chatgpt_response)

            # 3. Claude (실행) - Gemini + ChatGPT 결과 활용
            claude_context = {
                **context,
                "gemini_result": (
                    gemini_response.content if gemini_response.success else ""
                ),
                "chatgpt_result": (
                    chatgpt_response.content if chatgpt_response.success else ""
                ),
            }
            claude_response = await self.agents[2].query(question, claude_context)
            responses.append(claude_response)

        except Exception as e:
            logger.error(f"에이전트 실행 오류: {e}", exc_info=True)

        return responses

    def _create_fallback_synthesis(self, responses: List[AgentResponse]) -> str:
        """통합 실패시 기본 포맷 생성"""
        parts = ["# AI 협업 분석 결과\n\n"]

        for response in responses:
            emoji = "✅" if response.success else "❌"
            parts.append(f"## {emoji} {response.agent_name.title()}\n")
            parts.append(
                response.content
                if response.success
                else f"*응답 실패: {response.error}*"
            )
            parts.append("\n\n---\n\n")

        return "".join(parts)

    async def health_check_all(self) -> Dict[str, bool]:
        """모든 에이전트 상태 확인"""
        results = {}
        for agent in self.agents:
            results[agent.name] = await agent.health_check()
        return results
