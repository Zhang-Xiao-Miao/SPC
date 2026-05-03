from __future__ import annotations

from typing import Dict

from plan_b.io_utils import read_json


def summarize_pass(path: str) -> Dict[str, float]:
    payload = read_json(path)
    num_episodes = payload["num_episodes"]
    passed = sum(1 for row in payload["episodes"] if row["passed"])
    return {"pass@1": passed / max(num_episodes, 1)}

