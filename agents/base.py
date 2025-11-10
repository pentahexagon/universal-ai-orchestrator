"""
Base AI Agent interface
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from models.agent_response import AgentResponse as ModelAgentResponse


class AgentResponse:
    """Standardized response container returned by agents (simple version)."""

    def __init__(
        self, success: bool, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "metadata": self.metadata,
        }


class AgentBase(ABC):
    """Abstract base class for AI agents (simple skeleton version)."""

    name: str = "base-agent"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    async def prepare(self) -> None:
        """Optional async setup (e.g., warmup, model selection)."""
        return None

    @abstractmethod
    async def ask(self, prompt: str, **kwargs) -> AgentResponse:
        """Send a prompt to the agent and return a standardized AgentResponse."""
        raise NotImplementedError

    async def teardown(self) -> None:
        """Optional cleanup."""
        return None

    @property
    def short_name(self) -> str:
        return self.name


class AIAgent(ABC):
    """
    모든 AI 에이전트가 구현해야 하는 추상 인터페이스
    """

    def __init__(self, api_key: str, config: Dict[str, Any]):
        """
        Args:
            api_key: API 키
            config: 에이전트별 설정
        """
        self.api_key = api_key
        self.config = config
        self.name = self.__class__.__name__.replace("Agent", "").lower()

    @abstractmethod
    async def query(
        self, question: str, context: Optional[Dict] = None
    ) -> ModelAgentResponse:
        """
        질문에 대한 응답 생성

        Args:
            question: 사용자 질문
            context: 추가 컨텍스트 (카테고리, 다른 에이전트 결과 등)

        Returns:
            AgentResponse 객체
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        API 연결 상태 확인

        Returns:
            연결 성공 여부
        """
        pass

    def get_role(self) -> str:
        """
        에이전트 역할 설명 반환

        Returns:
            역할 문자열
        """
        return self.config.get("role", "AI 에이전트")
