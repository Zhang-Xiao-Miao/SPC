from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


ACTION_ORDER = ["A0_no_prior_mbr", "A1_weak_prior_mbr", "A2_single_prior_mbr", "A3_multi_prior_mbr"]


@dataclass
class SelectorRow:
    query_id: str
    features: List[float]
    action_labels: Dict[str, int]
    best_action: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "query_id": self.query_id,
            "features": self.features,
            "action_labels": self.action_labels,
            "best_action": self.best_action,
        }


def choose_best_action(action_labels: Dict[str, int]) -> str:
    ranked = sorted(ACTION_ORDER, key=lambda name: (-int(action_labels.get(name, 0)), ACTION_ORDER.index(name)))
    return ranked[0]


def build_feature_vector(reference_row: Dict[str, object], action_rows: Dict[str, Dict[str, object]]) -> List[float]:
    gate_features = reference_row.get("gate_features", {})
    candidates = reference_row.get("candidates", [])
    compile_rate = 0.0
    if candidates:
        compile_rate = sum(1 for cand in candidates if cand.get("compile_ok")) / len(candidates)
    return [
        float(gate_features.get("mean_entropy", 0.0)),
        float(gate_features.get("mean_retrieval", 0.0)),
        float(gate_features.get("max_prior_score", 0.0)),
        float(reference_row.get("structure_fidelity", 0.0)),
        float(compile_rate),
        float(reference_row.get("num_candidates", 0.0)),
    ]


def evaluate_predictions(rows: List[SelectorRow], predicted_actions: List[str]) -> Dict[str, float]:
    selected = []
    oracle = []
    always_on = []
    threshold = []
    for row, pred in zip(rows, predicted_actions):
        selected.append(int(row.action_labels.get(pred, 0)))
        oracle.append(max(row.action_labels.values()))
        always_on.append(int(row.action_labels.get("A3_multi_prior_mbr", 0)))
        threshold.append(int(getattr(row, "threshold_label", row.action_labels.get("A3_multi_prior_mbr", 0))))
    count = max(len(rows), 1)
    return {
        "selector_pass_rate": sum(selected) / count,
        "oracle_pass_rate": sum(oracle) / count,
        "always_on_pass_rate": sum(always_on) / count,
        "threshold_like_pass_rate": sum(threshold) / count,
    }
