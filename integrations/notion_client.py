"""
Notion API Client
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from notion_client import AsyncClient
from notion_client.errors import APIResponseError

from models.question import Question, QuestionStatus
from utils.logger import get_logger
from utils.retry import async_retry
from utils.rate_limiter import rate_limiters

logger = get_logger(__name__)


class NotionClient:
    """
    Notion API 통합 클라이언트
    """

    def __init__(self, api_key: str, inbox_db_id: str, results_db_id: str):
        """
        Args:
            api_key: Notion API 키
            inbox_db_id: Inbox 데이터베이스 ID
            results_db_id: Results 데이터베이스 ID
        """
        self.client = AsyncClient(auth=api_key)
        self.inbox_db_id = inbox_db_id
        self.results_db_id = results_db_id

    @async_retry(max_attempts=3, delay=1.0)
    async def query_pending_questions(self) -> List[Question]:
        """
        Inbox에서 status='pending' 질문 조회

        Returns:
            Question 객체 리스트
        """
        await rate_limiters['notion'].acquire()

        try:
            response = await self.client.databases.query(
                database_id=self.inbox_db_id,
                filter={
                    "property": "상태",
                    "status": {
                        "equals": "pending"
                    }
                },
                sorts=[
                    {
                        "property": "우선순위",
                        "direction": "ascending"
                    },
                    {
                        "timestamp": "created_time",
                        "direction": "ascending"
                    }
                ]
            )

            questions = []
            for page in response['results']:
                try:
                    question = Question.from_notion_page(page)
                    questions.append(question)
                except Exception as e:
                    logger.error(f"질문 파싱 실패 (page_id={page['id']}): {e}")

            logger.info(f"📥 {len(questions)}개 pending 질문 발견")
            return questions

        except APIResponseError as e:
            logger.error(f"Notion API 오류: {e}")
            raise

    @async_retry(max_attempts=3, delay=1.0)
    async def update_question_status(
        self,
        page_id: str,
        status: QuestionStatus,
        result_url: Optional[str] = None
    ):
        """
        Inbox 페이지 상태 업데이트

        Args:
            page_id: Notion 페이지 ID
            status: 새 상태
            result_url: 결과 페이지 URL (optional)
        """
        await rate_limiters['notion'].acquire()

        properties = {
            "상태": {
                "status": {
                    "name": status.value
                }
            }
        }

        # 결과 링크 추가
        if result_url:
            properties["결과링크"] = {
                "url": result_url
            }

        try:
            await self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            logger.info(f"✅ 상태 업데이트: {page_id} → {status.value}")

        except APIResponseError as e:
            logger.error(f"상태 업데이트 실패 (page_id={page_id}): {e}")
            raise

    @async_retry(max_attempts=3, delay=2.0)
    async def create_result_page(
        self,
        question: Question,
        responses: Dict[str, Dict],
        synthesis: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Results 데이터베이스에 결과 페이지 생성

        Args:
            question: 원본 질문
            responses: AI 에이전트 응답들
            synthesis: 통합 분석
            metadata: 메타데이터

        Returns:
            {'id': '...', 'url': '...'}
        """
        await rate_limiters['notion'].acquire()

        try:
            # Properties
            properties = {
                "제목": {
                    "title": [
                        {
                            "text": {
                                "content": question.text[:100]
                            }
                        }
                    ]
                },
                "카테고리": {
                    "select": {
                        "name": question.category or "기타"
                    }
                },
                "처리시간": {
                    "number": metadata.get('total_duration', 0)
                },
                "성공 에이전트": {
                    "number": metadata.get('successful_agents', 0)
                }
            }

            # Page content (blocks)
            children = self._create_result_blocks(
                question, responses, synthesis, metadata
            )

            # 페이지 생성
            page = await self.client.pages.create(
                parent={"database_id": self.results_db_id},
                properties=properties,
                children=children
            )

            result = {
                'id': page['id'],
                'url': page['url']
            }

            logger.info(f"✅ 결과 페이지 생성: {result['url']}")
            return result

        except APIResponseError as e:
            logger.error(f"결과 페이지 생성 실패: {e}")
            raise

    def _create_result_blocks(
        self,
        question: Question,
        responses: Dict[str, Dict],
        synthesis: str,
        metadata: Dict[str, Any]
    ) -> List[Dict]:
        """Notion 페이지 블록 생성"""
        blocks = []

        # 1. 원본 질문
        blocks.extend([
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "📝 원본 질문"}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {"type": "text", "text": {"content": question.text}}
                    ],
                    "color": "blue_background"
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ])

        # 2. 통합 분석 (주요 섹션)
        blocks.extend([
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "🎯 통합 분석"}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": synthesis[:2000]}}
                    ]
                }
            }
        ])

        # 구분선
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

        # 3. 개별 AI 응답
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {"type": "text", "text": {"content": "🤖 개별 AI 응답"}}
                ]
            }
        })

        agent_emojis = {
            'gemini': '🔍',
            'chatgpt': '💡',
            'claude': '✅'
        }

        for agent_name, response in responses.items():
            emoji = agent_emojis.get(agent_name, '🤖')
            status_emoji = "✅" if response['success'] else "❌"

            blocks.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"{emoji} {agent_name.upper()} {status_emoji}"}}
                    ],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": response['content'][:2000] if response['success'] else f"오류: {response.get('error', '알 수 없음')}"}}
                                ]
                            }
                        }
                    ]
                }
            })

        # 4. 메타데이터
        blocks.extend([
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "📊 처리 정보"}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"처리 시간: {metadata.get('total_duration', 0):.1f}초"}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"성공 에이전트: {metadata.get('successful_agents', 0)}/{metadata.get('total_agents', 3)}"}}
                    ]
                }
            }
        ])

        return blocks

    async def health_check(self) -> bool:
        """Notion API 연결 상태 확인"""
        try:
            await self.client.users.me()
            return True
        except:
            return False
