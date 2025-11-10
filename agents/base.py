"""Agent base interface for Universal AI Orchestrator.

Each agent (Gemini, ChatGPT, Claude) should implement AgentBase.
Supports async usage patterns and lifecycle hooks.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AgentResponse:
    """Standardized response container returned by agents."""

    def __init__(self, success: bool, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"success": self.success, "content": self.content, "metadata": self.metadata}


class AgentBase(ABC):
    """Abstract base class for AI agents."""

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
