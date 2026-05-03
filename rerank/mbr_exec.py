from __future__ import annotations

from typing import List, Tuple

from plan_b.schema import GenerationCandidate
from rerank.sandbox_runner import run_candidate


def rerank_candidates(candidates: List[GenerationCandidate], tests: str, timeout_sec: int = 5) -> Tuple[GenerationCandidate, List[GenerationCandidate]]:
    best = None
    best_score = -1.0
    for candidate in candidates:
        result = run_candidate(candidate.code, tests, timeout_sec=timeout_sec)
        candidate.exec_status = str(result["status"])
        candidate.passed = bool(result["passed"])
        candidate.details.update(result)
        candidate.compile_ok = result["status"] != "failed" or candidate.passed
        score = 1.0 if candidate.passed else 0.0
        if score > best_score:
            best = candidate
            best_score = score
    if best is None:
        best = GenerationCandidate(code="", source="empty", prior_name=None, score=0.0)
    return best, candidates

