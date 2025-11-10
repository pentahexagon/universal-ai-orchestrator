# integrations/notion_client_stub.py
"""Simple Notion client stub for testing and demonstration purposes."""

from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional


class NotionClientStub:
    """Minimal Notion client stub that simulates basic operations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        inbox_db_id: Optional[str] = None,
        results_db_id: Optional[str] = None,
    ):
        self.api_key = api_key
        self.inbox_db_id = inbox_db_id
        self.results_db_id = results_db_id

    async def query_pending_questions(self) -> List[Dict[str, Any]]:
        """Simulate fetching pending questions from Notion."""
        await asyncio.sleep(0.01)
        return [
            {
                "id": "test-question-1",
                "text": "Sample question from Notion Inbox",
                "category": "general",
                "priority": "medium",
                "status": "pending",
            }
        ]

    async def update_question_status(
        self, page_id: str, status: str, result_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simulate updating question status in Notion."""
        await asyncio.sleep(0.01)
        return {"success": True, "page_id": page_id, "status": status}

    async def create_result_page(
        self, question: Dict[str, Any], responses: Dict[str, Any], synthesis: str
    ) -> Dict[str, str]:
        """Simulate creating a result page in Notion."""
        await asyncio.sleep(0.01)
        return {
            "id": f"result-{question['id']}",
            "url": f"https://notion.so/result-{question['id']}",
        }

    async def health_check(self) -> bool:
        """Simulate health check."""
        await asyncio.sleep(0.01)
        return True
