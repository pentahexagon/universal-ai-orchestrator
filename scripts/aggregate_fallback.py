#!/usr/bin/env python3
"""
AI 응답 집계 및 합의 도출 스크립트

여러 AI 에이전트의 응답을 읽어서 합의를 도출하고 최선의 답변을 선택합니다.

사용법:
    python scripts/aggregate_fallback.py data/ai_responses.jsonl out/consensus_fallback.jsonl
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter


def load_responses(input_file: Path) -> List[Dict[str, Any]]:
    """JSONL 파일에서 AI 응답 로드"""
    responses = []
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                responses.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping invalid JSON at line {line_num}: {e}")

    return responses


def calculate_consensus(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    여러 응답에서 합의 도출

    전략:
    1. 성공한 응답만 사용
    2. 가장 긴 응답 선택 (더 상세한 정보)
    3. 공통 키워드 추출
    """
    # 성공한 응답만 필터링
    successful = [r for r in responses if r.get("success", False)]

    if not successful:
        return {
            "success": False,
            "error": "No successful responses",
            "consensus": None,
            "total_responses": len(responses),
            "successful_responses": 0,
        }

    # 가장 긴 응답 찾기
    best_response = max(successful, key=lambda r: len(r.get("content", "")))

    # 모든 에이전트 이름 수집
    agents = [r.get("agent_name", "unknown") for r in successful]
    agent_counts = Counter(agents)

    # 합의 결과
    consensus = {
        "success": True,
        "content": best_response.get("content", ""),
        "selected_agent": best_response.get("agent_name", "unknown"),
        "consensus_method": "longest_response",
        "total_responses": len(responses),
        "successful_responses": len(successful),
        "failed_responses": len(responses) - len(successful),
        "agent_distribution": dict(agent_counts),
        "metadata": {
            "selected_length": len(best_response.get("content", "")),
            "avg_length": sum(len(r.get("content", "")) for r in successful)
            / len(successful),
        },
    }

    return consensus


def aggregate_by_question(responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """질문별로 응답을 그룹화하고 합의 도출"""
    # 질문 ID나 텍스트로 그룹화
    grouped = {}

    for response in responses:
        question_id = response.get("question_id") or response.get("question", "unknown")

        if question_id not in grouped:
            grouped[question_id] = {
                "question_id": question_id,
                "question": response.get("question", ""),
                "responses": [],
            }

        grouped[question_id]["responses"].append(response)

    # 각 그룹에 대해 합의 도출
    results = []
    for question_id, data in grouped.items():
        consensus = calculate_consensus(data["responses"])
        result = {
            "question_id": question_id,
            "question": data["question"],
            "consensus": consensus,
            "original_responses": data["responses"],
        }
        results.append(result)

    return results


def save_results(results: List[Dict[str, Any]], output_file: Path):
    """결과를 JSONL로 저장"""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"✓ Saved {len(results)} consensus results to {output_file}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/aggregate_fallback.py <input.jsonl> <output.jsonl>")
        print("\nExample:")
        print(
            "  python scripts/aggregate_fallback.py data/ai_responses.jsonl out/consensus_fallback.jsonl"
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    print(f"Loading responses from {input_file}...")
    responses = load_responses(input_file)
    print(f"✓ Loaded {len(responses)} responses")

    print("Aggregating responses and calculating consensus...")
    results = aggregate_by_question(responses)
    print(f"✓ Processed {len(results)} unique questions")

    print(f"Saving results to {output_file}...")
    save_results(results, output_file)

    # 요약 통계
    total_success = sum(
        1 for r in results if r["consensus"].get("success", False)
    )
    print(f"\n📊 Summary:")
    print(f"  Total questions: {len(results)}")
    print(f"  Successful consensus: {total_success}")
    print(f"  Failed consensus: {len(results) - total_success}")


if __name__ == "__main__":
    main()
