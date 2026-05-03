from __future__ import annotations

from typing import Dict, Optional

from rerank.sandbox_runner import run_candidate


def build_quick_smoke_test(entry_point: str, arity: int) -> str:
    args = ", ".join("0" for _ in range(max(arity, 0)))
    return "\n".join(
        [
            f"result = {entry_point}({args})",
            "assert result is not None",
        ]
    )


def run_quick_runtime_check(code: str, entry_point: str, expected_arity: Optional[int], timeout_sec: int = 2) -> Dict[str, object]:
    if expected_arity is None:
        return {"status": "skipped", "passed": False}
    test = build_quick_smoke_test(entry_point, expected_arity)
    result = run_candidate(code, test, timeout_sec=timeout_sec)
    return {
        "status": result.get("status"),
        "passed": bool(result.get("passed")),
        "stderr": result.get("stderr", ""),
    }
