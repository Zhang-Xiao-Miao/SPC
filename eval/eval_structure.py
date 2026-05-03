from __future__ import annotations

from typing import Dict

from plan_b.io_utils import read_json


def summarize_structure(path: str) -> Dict[str, float]:
    payload = read_json(path)
    values = [row["structure_fidelity"] for row in payload["episodes"]]
    return {"mean_structure_fidelity": sum(values) / max(len(values), 1)}

