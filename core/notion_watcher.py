"""
Notion Watcher Service
"""

import asyncio
from datetime import datetime
from typing import Set, Callable, Awaitable
from integrations.notion_client import NotionClient
from models.question import Question, QuestionStatus
from utils.logger import get_logger

logger = get_logger(__name__)


class NotionWatcher:
    """
    Notion Inbox 데이터베이스 모니터링 서비스
    """

    def __init__(
        self,
        notion_client: NotionClient,
        polling_interval: int = 30,
        max_concurrent_tasks: int = 5,
    ):
        """
        Args:
            notion_client: NotionClient 인스턴스
            polling_interval: 폴링 간격 (초)
            max_concurrent_tasks: 동시 처리 가능한 질문 수
        """
        self.notion = notion_client
        self.polling_interval = polling_interval
        self.max_concurrent_tasks = max_concurrent_tasks

        # 처리 중인 질문 추적 (중복 방지)
        self.processing_ids: Set[str] = set()

        # 처리 완료한 질문 추적
        self.processed_ids: Set[str] = set()

        self.is_running = False

    async def start(self, callback: Callable[[Question], Awaitable[None]]):
        """
        감시 시작

        Args:
            callback: 질문 발견시 호출할 비동기 함수
                     async def process(question: Question) -> None
        """
        self.is_running = True
        logger.info(f"👀 Notion Watcher 시작 (간격: {self.polling_interval}초)")

        while self.is_running:
            try:
                # 1. Pending 질문 조회
                questions = await self.notion.query_pending_questions()

                # 2. 새로운 질문만 필터링
                new_questions = [
                    q
                    for q in questions
                    if q.page_id not in self.processing_ids
                    and q.page_id not in self.processed_ids
                ]

                if new_questions:
                    logger.info(f"🆕 {len(new_questions)}개 새 질문 발견")

                    # 3. 동시 처리 제한
                    semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

                    async def process_with_semaphore(question: Question):
                        async with semaphore:
                            await self._process_question(question, callback)

                    # 4. 병렬 처리
                    await asyncio.gather(
                        *[process_with_semaphore(q) for q in new_questions],
                        return_exceptions=True,
                    )

                # 5. 다음 폴링까지 대기
                await asyncio.sleep(self.polling_interval)

            except Exception as e:
                logger.error(f"❌ Watcher 오류: {e}", exc_info=True)
                await asyncio.sleep(self.polling_interval)

    async def _process_question(
        self, question: Question, callback: Callable[[Question], Awaitable[None]]
    ):
        """개별 질문 처리"""
        page_id = question.page_id

        try:
            # 처리 중 표시
            self.processing_ids.add(page_id)

            # 상태 업데이트: pending → processing
            await self.notion.update_question_status(
                page_id=page_id, status=QuestionStatus.PROCESSING
            )

            logger.info(f"🔄 처리 시작: {question.text[:50]}...")

            # 실제 처리 (Orchestrator)
            await callback(question)

            # 처리 완료
            self.processed_ids.add(page_id)
            logger.info(f"✅ 처리 완료: {page_id}")

        except Exception as e:
            logger.error(f"❌ 처리 실패 ({page_id}): {e}", exc_info=True)

            # 상태 업데이트: processing → failed
            try:
                await self.notion.update_question_status(
                    page_id=page_id, status=QuestionStatus.FAILED
                )
            except:
                pass

        finally:
            # 처리 중 표시 제거
            self.processing_ids.discard(page_id)

    def stop(self):
        """감시 중지"""
        logger.info("🛑 Notion Watcher 중지 요청")
        self.is_running = False

    def reset_processed(self):
        """처리 완료 기록 초기화"""
        self.processed_ids.clear()
        logger.info("🔄 처리 기록 초기화")
