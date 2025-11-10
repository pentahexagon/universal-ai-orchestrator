"""
Universal AI Orchestrator - Main Entry Point
"""

import asyncio
import signal
from config.settings import ConfigManager
from core.orchestrator import Orchestrator
from core.notion_watcher import NotionWatcher
from integrations.notion_client import NotionClient
from models.question import Question, QuestionStatus
from utils.logger import get_logger

logger = get_logger(__name__)


class Application:
    """
    메인 애플리케이션
    """

    def __init__(self):
        # 설정 로드
        self.config = ConfigManager()

        # Notion 클라이언트
        self.notion = NotionClient(
            api_key=self.config["api_keys"]["notion"],
            inbox_db_id=self.config["notion_db_ids"]["inbox"],
            results_db_id=self.config["notion_db_ids"]["results"],
        )

        # Orchestrator
        self.orchestrator = Orchestrator(self.config.config)

        # Watcher
        self.watcher = NotionWatcher(
            notion_client=self.notion,
            polling_interval=self.config.get("system.polling_interval", 30),
            max_concurrent_tasks=self.config.get("system.max_concurrent_tasks", 5),
        )

    async def start(self):
        """애플리케이션 시작"""
        logger.info("🚀 Universal AI Orchestrator 시작")

        # Health check
        logger.info("🔍 시스템 상태 확인 중...")
        if not await self._health_check():
            logger.error("❌ 시스템 상태 확인 실패")
            return

        logger.info("✅ 모든 시스템 정상")

        # Graceful shutdown 핸들러
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        # Watcher 시작
        try:
            await self.watcher.start(callback=self.process_question)
        except Exception as e:
            logger.error(f"❌ Watcher 오류: {e}", exc_info=True)

    async def process_question(self, question: Question):
        """
        질문 처리 콜백
        """
        try:
            # Orchestrator로 처리
            result = await self.orchestrator.process_question(
                question=question.text,
                context={
                    "category": question.category,
                    "priority": question.priority.value,
                },
            )

            if result["success"]:
                # 결과 페이지 생성
                result_page = await self.notion.create_result_page(
                    question=question,
                    responses=result["responses"],
                    synthesis=result["synthesis"],
                    metadata=result["metadata"],
                )

                # Inbox 상태 업데이트
                await self.notion.update_question_status(
                    page_id=question.page_id,
                    status=QuestionStatus.COMPLETED,
                    result_url=result_page["url"],
                )

                logger.info(f"✅ 완료: {result_page['url']}")
            else:
                # 실패 처리
                await self.notion.update_question_status(
                    page_id=question.page_id, status=QuestionStatus.FAILED
                )

        except Exception as e:
            logger.error(f"질문 처리 오류: {e}", exc_info=True)
            raise

    async def _health_check(self) -> bool:
        """시스템 헬스 체크"""
        checks = []

        # Notion
        notion_ok = await self.notion.health_check()
        checks.append(("Notion", notion_ok))

        # AI Agents
        agent_status = await self.orchestrator.health_check_all()
        for agent_name, status in agent_status.items():
            checks.append((agent_name.upper(), status))

        # 결과 출력
        for name, ok in checks:
            status = "✅" if ok else "❌"
            logger.info(f"{status} {name}")

        return all(ok for _, ok in checks)

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 종료 중...")
        self.watcher.stop()
        await asyncio.sleep(2)  # 진행 중인 작업 완료 대기
        logger.info("👋 종료 완료")


async def main():
    """메인 진입점"""
    app = Application()
    await app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 사용자 종료")
