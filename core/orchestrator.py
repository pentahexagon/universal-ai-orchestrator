"""Simple Orchestrator skeleton for Universal AI Orchestrator.

This is a minimal, testable class that coordinates agents and Notion integration.
Adapt and expand per your project needs.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional

from agents.base import AgentBase, AgentResponse


class Orchestrator:
    def __init__(
        self, agents: List[AgentBase], config: Optional[Dict[str, Any]] = None
    ):
        self.agents = agents
        self.config = config or {}

    async def run_once(self, prompt: str) -> Dict[str, Any]:
        """Run the pipeline once: ask each agent sequentially and collect results."""
        results: Dict[str, Any] = {"start": time.time(), "agents": []}
        for agent in self.agents:
            try:
                await agent.prepare()
                resp: AgentResponse = await agent.ask(prompt)
                results["agents"].append(
                    {"agent": agent.short_name, "response": resp.to_dict()}
                )
            except Exception as e:
                results["agents"].append(
                    {"agent": getattr(agent, "short_name", "unknown"), "error": str(e)}
                )
            finally:
                await agent.teardown()
        results["end"] = time.time()
        return results

    async def run_many(
        self, prompts: List[str], concurrency: int = 2
    ) -> List[Dict[str, Any]]:
        """Run multiple prompts with a concurrency limit."""
        sem = asyncio.Semaphore(concurrency)

        async def worker(p):
            async with sem:
                return await self.run_once(p)

        return await asyncio.gather(*(worker(p) for p in prompts))
