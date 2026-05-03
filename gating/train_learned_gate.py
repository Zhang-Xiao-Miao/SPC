from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

from gating.calibration import brier_score, expected_calibration_error
from plan_b.io_utils import read_json, write_json


def load_features_and_labels(prior_path: str, baseline_path: str):
    prior = read_json(prior_path)
    baseline = read_json(baseline_path)
    baseline_by_id = {row["episode"]["query_id"]: row for row in baseline["episodes"]}
    features = []
    labels = []
    query_ids = []
    baseline_labels = []
    for row in prior["episodes"]:
        query_id = row["episode"]["query_id"]
        base_row = baseline_by_id[query_id]
        feats = row.get("gate_features", {})
        features.append(
            [
                float(feats.get("mean_entropy", 0.0)),
                float(feats.get("mean_retrieval", 0.0)),
                float(feats.get("max_prior_score", 0.0)),
                float(feats.get("num_supports", 0.0)),
                float(feats.get("num_candidates", 0.0)),
                float(row.get("structure_fidelity", 0.0)),
            ]
        )
        labels.append(1 if row["passed"] else 0)
        baseline_labels.append(1 if base_row["passed"] else 0)
        query_ids.append(query_id)
    return features, labels, baseline_labels, query_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a learned gate from prior-run diagnostics.")
    parser.add_argument("--prior-run", required=True)
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--output", default="results/learned_gate_metrics.json")
    args = parser.parse_args()

    X, y, baseline_y, query_ids = load_features_and_labels(args.prior_run, args.baseline_run)
    kf = KFold(n_splits=5, shuffle=True, random_state=1)
    probs = [0.5 for _ in X]
    for train_idx, test_idx in kf.split(X):
        model = LogisticRegression(max_iter=500)
        x_train = [X[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]
        x_test = [X[i] for i in test_idx]
        model.fit(x_train, y_train)
        pred = model.predict_proba(x_test)[:, 1].tolist()
        for idx, prob in zip(test_idx, pred):
            probs[idx] = prob

    learned_decisions = [1 if prob >= 0.5 else 0 for prob in probs]
    combined = []
    for use_prior, prior_label, base_label in zip(learned_decisions, y, baseline_y):
        combined.append(prior_label if use_prior else base_label)

    payload = {
        "num_examples": len(X),
        "ece": expected_calibration_error(probs, y),
        "brier": brier_score(probs, y),
        "prior_pass_rate": sum(y) / len(y),
        "baseline_pass_rate": sum(baseline_y) / len(baseline_y),
        "learned_gate_pass_rate": sum(combined) / len(combined),
        "coverage": sum(learned_decisions) / len(learned_decisions),
        "rows": [
            {
                "query_id": query_id,
                "prob_use_prior": prob,
                "use_prior": int(use_prior),
                "prior_pass": int(prior_label),
                "baseline_pass": int(base_label),
                "combined_pass": int(final_label),
            }
            for query_id, prob, use_prior, prior_label, base_label, final_label in zip(
                query_ids, probs, learned_decisions, y, baseline_y, combined
            )
        ],
    }
    write_json(args.output, payload)


if __name__ == "__main__":
    main()
