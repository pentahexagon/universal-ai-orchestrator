"""Test Orchestrator with agent skeletons."""

from __future__ import annotations
import asyncio
import pytest

from core.orchestrator import Orchestrator
from agents.gemini import GeminiAgent
from agents.chatgpt import ChatGPTAgent
from agents.claude import ClaudeAgent


@pytest.mark.asyncio
async def test_orchestrator_run_once():
    """Test that Orchestrator can run with skeleton agents."""
    agents = [
        GeminiAgent(config={"model": "gemini-pro"}),
        ChatGPTAgent(config={"model": "gpt-4"}),
        ClaudeAgent(config={"model": "claude-sonnet-4-5"}),
    ]

    orchestrator = Orchestrator(agents=agents, config={})
    result = await orchestrator.run_once("Test prompt")

    assert "start" in result
    assert "end" in result
    assert "agents" in result
    assert len(result["agents"]) == 3

    # Check all agents succeeded
    for agent_result in result["agents"]:
        assert "agent" in agent_result
        assert "response" in agent_result
        response = agent_result["response"]
        assert response["success"] is True
        assert "simulated" in response["content"]


@pytest.mark.asyncio
async def test_orchestrator_run_many():
    """Test that Orchestrator can run multiple prompts concurrently."""
    agents = [
        GeminiAgent(config={"model": "gemini-pro"}),
        ChatGPTAgent(config={"model": "gpt-4"}),
    ]

    orchestrator = Orchestrator(agents=agents, config={})
    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    results = await orchestrator.run_many(prompts, concurrency=2)

    assert len(results) == 3
    for result in results:
        assert "start" in result
        assert "end" in result
        assert len(result["agents"]) == 2


@pytest.mark.asyncio
async def test_agent_lifecycle_hooks():
    """Test that agent prepare and teardown hooks are called."""

    class TrackedAgent(GeminiAgent):
        prepare_called = False
        teardown_called = False

        async def prepare(self):
            self.prepare_called = True

        async def teardown(self):
            self.teardown_called = True

    agent = TrackedAgent()
    orchestrator = Orchestrator(agents=[agent], config={})

    await orchestrator.run_once("Test")

    assert agent.prepare_called is True
    assert agent.teardown_called is True
