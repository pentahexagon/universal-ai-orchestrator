# agents/gemini_skeleton.py
from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional

from agents.base import AgentBase, AgentResponse


class GeminiAgent(AgentBase):
    name = "gemini"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config=config)

    async def ask(self, prompt: str, **kwargs) -> AgentResponse:
        # 간단한 목 구현 — 실제 API 호출으로 교체하세요.
        await asyncio.sleep(0.05)
        content = f"[Gemini simulated] {prompt}"
        return AgentResponse(
            success=True,
            content=content,
            metadata={"model": self.config.get("model", "gemini-pro")},
        )
