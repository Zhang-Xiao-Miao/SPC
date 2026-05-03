from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

from gating.calibration import brier_score, expected_calibration_error
from plan_b.io_utils import read_json, write_json


def load_rows(prior_path: str, baseline_path: str):
    prior = read_json(prior_path)
    baseline = read_json(baseline_path)
    baseline_by_id = {row["episode"]["query_id"]: row for row in baseline["episodes"]}
    rows = []
    for row in prior["episodes"]:
        query_id = row["episode"]["query_id"]
        base_row = baseline_by_id[query_id]
        feats = row.get("gate_features", {})
        rows.append(
            {
                "query_id": query_id,
                "features": [
                    float(feats.get("mean_entropy", 0.0)),
                    float(feats.get("mean_retrieval", 0.0)),
                    float(feats.get("max_prior_score", 0.0)),
                    float(feats.get("num_supports", 0.0)),
                    float(feats.get("num_candidates", 0.0)),
                    float(row.get("structure_fidelity", 0.0)),
                ],
                "prior_pass": int(row["passed"]),
                "baseline_pass": int(base_row["passed"]),
                "prefer_prior": int(row["passed"]) >= int(base_row["passed"]),
            }
        )
    return rows


def evaluate_threshold(rows, probs, threshold):
    decisions = [1 if prob >= threshold else 0 for prob in probs]
    combined = []
    for row, use_prior in zip(rows, decisions):
        combined.append(row["prior_pass"] if use_prior else row["baseline_pass"])
    return {
        "threshold": threshold,
        "coverage": sum(decisions) / len(decisions),
        "pass_rate": sum(combined) / len(combined),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a relative gate that predicts whether prior should replace baseline.")
    parser.add_argument("--prior-run", required=True)
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--output", default="results/relative_gate_metrics.json")
    args = parser.parse_args()

    rows = load_rows(args.prior_run, args.baseline_run)
    X = [row["features"] for row in rows]
    y = [row["prefer_prior"] for row in rows]
    probs = [0.5 for _ in rows]

    kf = KFold(n_splits=5, shuffle=True, random_state=1)
    for train_idx, test_idx in kf.split(X):
        x_train = [X[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]
        if len(set(y_train)) < 2:
            pred = [y_train[0] if y_train else 1.0 for _ in test_idx]
        else:
            model = LogisticRegression(max_iter=500, class_weight="balanced")
            model.fit(x_train, y_train)
            pred = model.predict_proba([X[i] for i in test_idx])[:, 1].tolist()
        for idx, prob in zip(test_idx, pred):
            probs[idx] = float(prob)

    sweep = [evaluate_threshold(rows, probs, round(i / 20, 2)) for i in range(1, 20)]
    best = max(sweep, key=lambda item: item["pass_rate"])
    payload = {
        "num_examples": len(rows),
        "prefer_prior_rate": sum(y) / len(y),
        "ece": expected_calibration_error(probs, y),
        "brier": brier_score(probs, y),
        "best_threshold": best["threshold"],
        "best_pass_rate": best["pass_rate"],
        "best_coverage": best["coverage"],
        "baseline_pass_rate": sum(row["baseline_pass"] for row in rows) / len(rows),
        "prior_pass_rate": sum(row["prior_pass"] for row in rows) / len(rows),
        "oracle_upper": sum(max(row["prior_pass"], row["baseline_pass"]) for row in rows) / len(rows),
        "threshold_sweep": sweep,
        "rows": [
            {
                "query_id": row["query_id"],
                "prob_prefer_prior": prob,
                "prefer_prior": row["prefer_prior"],
                "prior_pass": row["prior_pass"],
                "baseline_pass": row["baseline_pass"],
            }
            for row, prob in zip(rows, probs)
        ],
    }
    write_json(args.output, payload)


if __name__ == "__main__":
    main()
