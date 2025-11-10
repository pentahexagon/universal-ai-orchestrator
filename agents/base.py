"""
Base AI Agent interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from models.agent_response import AgentResponse


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
        self.name = self.__class__.__name__.replace('Agent', '').lower()

    @abstractmethod
    async def query(self, question: str, context: Optional[Dict] = None) -> AgentResponse:
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
        """에이전트의 역할 반환"""
        role_map = {
            'gemini': '정보 수집',
            'chatgpt': '분석 및 전략',
            'claude': '실행 계획'
        }
        return role_map.get(self.name, '미정의')
