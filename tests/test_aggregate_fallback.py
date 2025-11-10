"""Tests for aggregate_fallback.py script"""

import json
import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from aggregate_fallback import (
    calculate_consensus,
    aggregate_by_question,
)


def test_calculate_consensus_all_successful():
    """Test consensus calculation with all successful responses"""
    responses = [
        {
            "agent_name": "gemini",
            "success": True,
            "content": "Short answer",
        },
        {
            "agent_name": "chatgpt",
            "success": True,
            "content": "This is a much longer and more detailed answer",
        },
        {
            "agent_name": "claude",
            "success": True,
            "content": "Medium answer here",
        },
    ]

    result = calculate_consensus(responses)

    assert result["success"] is True
    assert result["selected_agent"] == "chatgpt"
    assert result["total_responses"] == 3
    assert result["successful_responses"] == 3
    assert result["failed_responses"] == 0
    assert "longer and more detailed" in result["content"]


def test_calculate_consensus_with_failures():
    """Test consensus calculation with some failed responses"""
    responses = [
        {
            "agent_name": "gemini",
            "success": True,
            "content": "Good answer",
        },
        {
            "agent_name": "chatgpt",
            "success": False,
            "error": "API timeout",
        },
        {
            "agent_name": "claude",
            "success": True,
            "content": "Another good answer that is longer",
        },
    ]

    result = calculate_consensus(responses)

    assert result["success"] is True
    assert result["selected_agent"] == "claude"
    assert result["total_responses"] == 3
    assert result["successful_responses"] == 2
    assert result["failed_responses"] == 1


def test_calculate_consensus_all_failed():
    """Test consensus calculation when all responses failed"""
    responses = [
        {
            "agent_name": "gemini",
            "success": False,
            "error": "API error",
        },
        {
            "agent_name": "chatgpt",
            "success": False,
            "error": "Timeout",
        },
    ]

    result = calculate_consensus(responses)

    assert result["success"] is False
    assert result["consensus"] is None
    assert result["total_responses"] == 2
    assert result["successful_responses"] == 0


def test_aggregate_by_question():
    """Test grouping responses by question"""
    responses = [
        {
            "question_id": "q1",
            "question": "What is AI?",
            "agent_name": "gemini",
            "success": True,
            "content": "AI is...",
        },
        {
            "question_id": "q1",
            "question": "What is AI?",
            "agent_name": "chatgpt",
            "success": True,
            "content": "Artificial Intelligence is...",
        },
        {
            "question_id": "q2",
            "question": "What is ML?",
            "agent_name": "claude",
            "success": True,
            "content": "Machine Learning is...",
        },
    ]

    results = aggregate_by_question(responses)

    assert len(results) == 2
    assert results[0]["question_id"] in ["q1", "q2"]
    assert results[1]["question_id"] in ["q1", "q2"]

    # Check that q1 has 2 responses
    q1_result = next(r for r in results if r["question_id"] == "q1")
    assert len(q1_result["original_responses"]) == 2


def test_aggregate_by_question_with_missing_id():
    """Test handling responses without question_id"""
    responses = [
        {
            "question": "Test question",
            "agent_name": "gemini",
            "success": True,
            "content": "Answer",
        }
    ]

    results = aggregate_by_question(responses)

    assert len(results) == 1
    assert results[0]["question_id"] == "Test question"


def test_consensus_metadata():
    """Test that consensus includes proper metadata"""
    responses = [
        {
            "agent_name": "agent1",
            "success": True,
            "content": "A" * 100,
        },
        {
            "agent_name": "agent2",
            "success": True,
            "content": "B" * 200,
        },
    ]

    result = calculate_consensus(responses)

    assert "metadata" in result
    assert "selected_length" in result["metadata"]
    assert "avg_length" in result["metadata"]
    assert result["metadata"]["selected_length"] == 200
    assert result["metadata"]["avg_length"] == 150.0


def test_agent_distribution():
    """Test agent distribution counting"""
    responses = [
        {"agent_name": "gemini", "success": True, "content": "A"},
        {"agent_name": "gemini", "success": True, "content": "B"},
        {"agent_name": "claude", "success": True, "content": "C"},
    ]

    result = calculate_consensus(responses)

    assert result["agent_distribution"]["gemini"] == 2
    assert result["agent_distribution"]["claude"] == 1
