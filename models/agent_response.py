"""
AI Agent Response data model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class AgentResponse:
    """
    AI 에이전트 응답 표준 포맷

    Attributes:
        agent_name: 에이전트 이름 ("gemini" | "chatgpt" | "claude")
        content: 응답 내용
        timestamp: 응답 생성 시각
        success: 성공 여부
        metadata: 메타데이터 (토큰 수, 소요 시간 등)
        error: 에러 메시지 (실패시)
    """
    agent_name: str
    content: str
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'agent_name': self.agent_name,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'metadata': self.metadata,
            'error': self.error
        }

    def __str__(self) -> str:
        """문자열 표현"""
        status = "✅" if self.success else "❌"
        return f"{status} {self.agent_name.upper()}: {self.content[:100]}..."
