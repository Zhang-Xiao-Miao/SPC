from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.action_selector import ACTION_ORDER, SelectorRow, build_feature_vector, choose_best_action
from plan_b.io_utils import read_json, write_jsonl


ACTION_TO_PATH_KEY = {
    "A0_no_prior_mbr": "no_prior",
    "A1_weak_prior_mbr": "weak_prior",
    "A2_single_prior_mbr": "single_prior",
    "A3_multi_prior_mbr": "multi_prior_mbr",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build action selector dataset from completed runs.")
    parser.add_argument("--no-prior", required=True)
    parser.add_argument("--weak-prior", required=True)
    parser.add_argument("--single-prior", required=True)
    parser.add_argument("--multi-prior-mbr", required=True)
    parser.add_argument("--threshold-run")
    parser.add_argument("--out", default="data/b_action_selector_dev.jsonl")
    args = parser.parse_args()

    runs = {
        "A0_no_prior_mbr": read_json(args.no_prior),
        "A1_weak_prior_mbr": read_json(args.weak_prior),
        "A2_single_prior_mbr": read_json(args.single_prior),
        "A3_multi_prior_mbr": read_json(args.multi_prior_mbr),
    }
    indexed = {}
    for action_name, run in runs.items():
        indexed[action_name] = {row["episode"]["query_id"]: row for row in run["episodes"]}
    threshold_index = None
    if args.threshold_run:
        threshold_run = read_json(args.threshold_run)
        threshold_index = {row["episode"]["query_id"]: row for row in threshold_run["episodes"]}
    query_ids = list(indexed["A3_multi_prior_mbr"].keys())
    rows = []
    for query_id in query_ids:
        action_rows = {action_name: index[query_id] for action_name, index in indexed.items()}
        reference = action_rows["A3_multi_prior_mbr"]
        action_labels = {action_name: int(row["passed"]) for action_name, row in action_rows.items()}
        features = build_feature_vector(reference, action_rows)
        row = SelectorRow(query_id=query_id, features=features, action_labels=action_labels, best_action=choose_best_action(action_labels)).to_dict()
        if threshold_index is not None:
            row["threshold_label"] = int(threshold_index[query_id]["passed"])
        rows.append(row)
    write_jsonl(args.out, rows)


if __name__ == "__main__":
    main()
