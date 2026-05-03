from __future__ import annotations

import math
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, average_precision_score, roc_auc_score

from guardrails.quick_runtime_check import run_quick_runtime_check
from guardrails.static_checks import infer_required_arity, run_static_checks
from plan_b.mbpp import load_examples


SMOKE_STATUS_ORDER = {
    "passed": 2.0,
    "skipped": 1.0,
    "timeout": -0.5,
    "failed": -1.0,
}


@dataclass
class CandidateFeatureRow:
    query_id: str
    entry_point: str
    candidate_index: int
    label: int
    features: List[float]
    feature_map: Dict[str, float]
    metadata: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class LearnedVerifierModel:
    feature_names: List[str]
    model: object

    def predict_scores(self, rows: Sequence[CandidateFeatureRow]) -> List[float]:
        matrix = [row.features for row in rows]
        if not matrix:
            return []
        if hasattr(self.model, "predict_proba"):
            return [float(score[1]) for score in self.model.predict_proba(matrix)]
        if hasattr(self.model, "decision_function"):
            raw = self.model.decision_function(matrix)
            return [1.0 / (1.0 + math.exp(-float(value))) for value in raw]
        return [float(value) for value in self.model.predict(matrix)]

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as handle:
            pickle.dump({"feature_names": self.feature_names, "model": self.model}, handle)

    @classmethod
    def load(cls, path: str | Path) -> "LearnedVerifierModel":
        with open(path, "rb") as handle:
            payload = pickle.load(handle)
        return cls(feature_names=list(payload["feature_names"]), model=payload["model"])


def load_eval_index(eval_examples_path: str | Path) -> Dict[str, object]:
    return {example.task_id: example for example in load_examples(eval_examples_path)}


def candidate_feature_map(
    candidate: Dict[str, object],
    episode_row: Dict[str, object],
    example: object,
    candidate_index: int,
    include_smoke: bool = False,
) -> Dict[str, float]:
    code = candidate.get("code", "")
    expected_arity = infer_required_arity(example.code)
    static = run_static_checks(code, entry_point=example.entry_point, prompt=example.prompt, expected_arity=expected_arity)
    smoke = {"status": "skipped", "passed": False}
    if include_smoke:
        smoke = run_quick_runtime_check(code, entry_point=example.entry_point, expected_arity=expected_arity, timeout_sec=2)
    details = candidate.get("details", {})
    gate = episode_row.get("gate_features", {})
    retrieval_scores = episode_row.get("retrieval_scores", [])
    feature_map = {
        "candidate_index": float(candidate_index),
        "has_prior": 0.0 if candidate.get("prior_name") in {None, "", "none"} else 1.0,
        "is_multi_prior": 1.0 if candidate.get("prior_name") == "multi_candidate" else 0.0,
        "source_is_retrieval_edit": 1.0 if candidate.get("source") == "retrieval_edit" else 0.0,
        "parse_ok": 1.0 if static.get("parse_ok") else 0.0,
        "function_name_ok": 1.0 if static.get("function_name_ok") else 0.0,
        "arity_ok": 1.0 if static.get("arity_ok") else 0.0,
        "return_type_ok": 1.0 if static.get("return_type_ok") else 0.0,
        "smoke_passed": 1.0 if smoke.get("passed") else 0.0,
        "smoke_status": SMOKE_STATUS_ORDER.get(str(smoke.get("status", "failed")), -1.0),
        "compile_ok": 1.0 if candidate.get("compile_ok") else 0.0,
        "exec_timeout": 1.0 if candidate.get("exec_status") == "timeout" else 0.0,
        "prompt_tokens": float(details.get("prompt_tokens", 0.0)),
        "completion_tokens": float(details.get("completion_tokens", 0.0)),
        "latency_sec": float(details.get("latency_sec", 0.0)),
        "structure_fidelity": float(episode_row.get("structure_fidelity", 0.0)),
        "mean_entropy": float(gate.get("mean_entropy", 0.0)),
        "mean_retrieval": float(gate.get("mean_retrieval", 0.0)),
        "max_prior_score": float(gate.get("max_prior_score", 0.0)),
        "num_supports": float(gate.get("num_supports", 0.0)),
        "num_candidates": float(episode_row.get("num_candidates", 0.0)),
        "retrieval_score_mean": float(sum(retrieval_scores) / max(len(retrieval_scores), 1)) if retrieval_scores else 0.0,
        "code_num_lines": float(len(code.splitlines())),
        "code_num_chars": float(len(code)),
        "code_has_return": 1.0 if "return" in code else 0.0,
    }
    return feature_map


def build_candidate_rows_from_run(
    run_payload: Dict[str, object],
    eval_examples_path: str | Path,
    include_smoke: bool = False,
) -> List[CandidateFeatureRow]:
    eval_index = load_eval_index(eval_examples_path)
    rows: List[CandidateFeatureRow] = []
    for episode_row in run_payload.get("episodes", []):
        query_id = episode_row.get("episode", {}).get("query_id")
        if query_id not in eval_index:
            continue
        example = eval_index[query_id]
        for candidate_index, candidate in enumerate(episode_row.get("candidates", [])):
            fmap = candidate_feature_map(candidate, episode_row, example, candidate_index, include_smoke=include_smoke)
            rows.append(
                CandidateFeatureRow(
                    query_id=query_id,
                    entry_point=example.entry_point,
                    candidate_index=candidate_index,
                    label=1 if candidate.get("passed") else 0,
                    features=list(fmap.values()),
                    feature_map=fmap,
                    metadata={
                        "prior_name": candidate.get("prior_name"),
                        "source": candidate.get("source"),
                        "exec_status": candidate.get("exec_status"),
                    },
                )
            )
    return rows


def stack_rows(rows: Sequence[CandidateFeatureRow]) -> tuple[List[str], List[List[float]], List[int]]:
    if not rows:
        return [], [], []
    feature_names = list(rows[0].feature_map.keys())
    matrix = [row.features for row in rows]
    labels = [row.label for row in rows]
    return feature_names, matrix, labels


def train_model(rows: Sequence[CandidateFeatureRow], random_state: int = 1) -> LearnedVerifierModel:
    feature_names, matrix, labels = stack_rows(rows)
    if not matrix:
        raise ValueError("No training rows were built for the verifier.")
    model = HistGradientBoostingClassifier(
        learning_rate=0.05,
        max_depth=6,
        max_iter=200,
        min_samples_leaf=20,
        random_state=random_state,
    )
    model.fit(matrix, labels)
    return LearnedVerifierModel(feature_names=feature_names, model=model)


def evaluate_model(model: LearnedVerifierModel, rows: Sequence[CandidateFeatureRow]) -> Dict[str, float]:
    _, matrix, labels = stack_rows(rows)
    if not matrix:
        return {"num_rows": 0}
    scores = model.predict_scores(rows)
    preds = [1 if score >= 0.5 else 0 for score in scores]
    metrics = {
        "num_rows": float(len(rows)),
        "positive_rate": sum(labels) / max(len(labels), 1),
        "accuracy": float(accuracy_score(labels, preds)),
        "average_precision": float(average_precision_score(labels, scores)),
    }
    if len(set(labels)) > 1:
        metrics["roc_auc"] = float(roc_auc_score(labels, scores))
    else:
        metrics["roc_auc"] = 0.0
    return metrics


def merge_rows(row_groups: Iterable[Sequence[CandidateFeatureRow]]) -> List[CandidateFeatureRow]:
    merged: List[CandidateFeatureRow] = []
    for rows in row_groups:
        merged.extend(rows)
    return merged
