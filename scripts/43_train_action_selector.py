from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold

from plan_b.action_selector import ACTION_ORDER, evaluate_predictions
from plan_b.io_utils import read_jsonl, write_json


def model_for_name(name: str):
    if name == "xgb":
        return RandomForestClassifier(n_estimators=200, random_state=1, class_weight="balanced")
    return LogisticRegression(max_iter=500, multi_class="auto")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a Plan B action selector.")
    parser.add_argument("--train", required=True)
    parser.add_argument("--dev", required=True)
    parser.add_argument("--model", default="xgb")
    parser.add_argument("--out", default="models/b_action_selector_xgb.json")
    parser.add_argument("--report-out", default="paper/b_week3_action_selector_table.md")
    parser.add_argument("--crossval-folds", type=int, default=5)
    args = parser.parse_args()

    train_rows = read_jsonl(args.train)
    dev_rows = read_jsonl(args.dev)
    action_to_index = {name: index for index, name in enumerate(ACTION_ORDER)}
    all_rows = train_rows + dev_rows
    x_all = [row["features"] for row in all_rows]
    y_all = [action_to_index[row["best_action"]] for row in all_rows]

    pred_all = [0 for _ in all_rows]
    if args.crossval_folds > 1 and len(all_rows) >= args.crossval_folds:
        kf = KFold(n_splits=args.crossval_folds, shuffle=True, random_state=1)
        for train_idx, test_idx in kf.split(x_all):
            model = model_for_name(args.model)
            model.fit([x_all[i] for i in train_idx], [y_all[i] for i in train_idx])
            fold_pred = model.predict([x_all[i] for i in test_idx]).tolist()
            for idx, pred in zip(test_idx, fold_pred):
                pred_all[idx] = pred
        final_model = model_for_name(args.model)
        final_model.fit(x_all, y_all)
    else:
        final_model = model_for_name(args.model)
        final_model.fit(x_all, y_all)
        pred_all = final_model.predict(x_all).tolist()

    pred_actions = [ACTION_ORDER[index] for index in pred_all]

    selector_eval = evaluate_predictions(
        rows=[
            type("Row", (), {
                "action_labels": row["action_labels"],
                "threshold_label": row.get("threshold_label"),
            })()
            for row in all_rows
        ],
        predicted_actions=pred_actions,
    )

    payload = {
        "model": args.model,
        "cv_accuracy": accuracy_score(y_all, pred_all),
        **selector_eval,
        "feature_dim": len(x_all[0]) if x_all else 0,
        "rows": [
            {
                "query_id": row["query_id"],
                "gold_action": row["best_action"],
                "pred_action": pred_action,
                "action_labels": row["action_labels"],
            }
            for row, pred_action in zip(all_rows, pred_actions)
        ],
    }
    if hasattr(final_model, "coef_"):
        payload["weights"] = {"bias": final_model.intercept_.tolist(), "coef": final_model.coef_.tolist()}
    if hasattr(final_model, "feature_importances_"):
        payload["feature_importances"] = final_model.feature_importances_.tolist()
    write_json(args.out, payload)

    md = "# Week3 Action Selector\n\n"
    md += "| Metric | Value |\n| --- | ---: |\n"
    for key in ["cv_accuracy", "selector_pass_rate", "always_on_pass_rate", "threshold_like_pass_rate", "oracle_pass_rate"]:
        md += f"| {key} | {payload[key]:.4f} |\n"
    Path(args.report_out).write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
