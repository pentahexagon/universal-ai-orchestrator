"""
Question data model
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class QuestionStatus(Enum):
    """질문 처리 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionPriority(Enum):
    """질문 우선순위"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Question:
    """
    Notion Inbox의 질문 데이터 모델

    Attributes:
        page_id: Notion 페이지 ID
        text: 질문 내용
        status: 처리 상태
        priority: 우선순위
        category: 카테고리 (optional)
        created_at: 생성 시각
        metadata: 추가 메타데이터
    """
    page_id: str
    text: str
    status: QuestionStatus
    priority: QuestionPriority = QuestionPriority.MEDIUM
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'page_id': self.page_id,
            'text': self.text,
            'status': self.status.value,
            'priority': self.priority.value,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_notion_page(cls, page: dict) -> 'Question':
        """
        Notion 페이지에서 Question 객체 생성

        Args:
            page: Notion API 응답 페이지 객체

        Returns:
            Question 인스턴스
        """
        props = page['properties']

        # 제목 추출
        title_prop = props.get('제목', {}).get('title', [])
        text = title_prop[0]['text']['content'] if title_prop else "Untitled"

        # 상태 추출
        status_prop = props.get('상태', {}).get('status', {}).get('name', 'pending')
        status = QuestionStatus(status_prop.lower())

        # 우선순위 추출
        priority_prop = props.get('우선순위', {}).get('select', {}).get('name', 'medium')
        priority = QuestionPriority(priority_prop.lower())

        # 카테고리 추출
        category_prop = props.get('카테고리', {}).get('select', {})
        category = category_prop.get('name') if category_prop else None

        # 생성 시각
        created_time = page.get('created_time')
        created_at = datetime.fromisoformat(created_time.replace('Z', '+00:00')) if created_time else None

        return cls(
            page_id=page['id'],
            text=text,
            status=status,
            priority=priority,
            category=category,
            created_at=created_at,
            metadata={}
        )
