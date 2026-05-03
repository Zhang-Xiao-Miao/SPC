from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.io_utils import read_json, write_json
from verifier.learned_verifier import (
    build_candidate_rows_from_run,
    evaluate_model,
    merge_rows,
    train_model,
)


def parse_run_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_config(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a lightweight learned verifier for Plan B.")
    parser.add_argument("--train-runs", required=True, help="Comma-separated run JSON files.")
    parser.add_argument("--dev-runs", required=True, help="Comma-separated run JSON files.")
    parser.add_argument("--eval-examples", default="data/processed/evalplus/mbppplus_test.jsonl")
    parser.add_argument("--config", default=None)
    parser.add_argument("--model-out", default="models/plan_b_learned_verifier.pkl")
    parser.add_argument("--out", default="results/plan_b_learned_verifier.json")
    args = parser.parse_args()

    config = load_config(args.config)
    include_smoke = bool(config.get("include_smoke", False))
    train_payloads = [read_json(path) for path in parse_run_list(args.train_runs)]
    dev_payloads = [read_json(path) for path in parse_run_list(args.dev_runs)]

    train_rows = merge_rows(
        build_candidate_rows_from_run(payload, args.eval_examples, include_smoke=include_smoke) for payload in train_payloads
    )
    dev_rows = merge_rows(
        build_candidate_rows_from_run(payload, args.eval_examples, include_smoke=include_smoke) for payload in dev_payloads
    )

    random_state = int(config.get("random_state", 1))
    model = train_model(train_rows, random_state=random_state)
    train_metrics = evaluate_model(model, train_rows)
    dev_metrics = evaluate_model(model, dev_rows)
    model.save(args.model_out)

    payload = {
        "config": config,
        "train_runs": parse_run_list(args.train_runs),
        "dev_runs": parse_run_list(args.dev_runs),
        "eval_examples": args.eval_examples,
        "model_out": args.model_out,
        "num_train_rows": len(train_rows),
        "num_dev_rows": len(dev_rows),
        "feature_names": model.feature_names,
        "include_smoke": include_smoke,
        "train_metrics": train_metrics,
        "dev_metrics": dev_metrics,
    }
    write_json(args.out, payload)


if __name__ == "__main__":
    main()
