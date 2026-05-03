from __future__ import annotations

from typing import Dict, List

from gating.calibration import brier_score, expected_calibration_error
from plan_b.io_utils import read_json


def summarize_risk(path: str) -> Dict[str, float]:
    payload = read_json(path)
    probs: List[float] = []
    labels: List[int] = []
    coverage = 0
    for row in payload["episodes"]:
        for gate_record in row["gate_records"]:
            probs.append(float(gate_record.get("mean_retrieval", 0.0)))
            labels.append(1 if row["passed"] else 0)
            if gate_record.get("use_prior"):
                coverage += 1
                break
    total = len(payload["episodes"])
    return {
        "risk_coverage": coverage / max(total, 1),
        "ece": expected_calibration_error(probs, labels),
        "brier": brier_score(probs, labels),
    }

