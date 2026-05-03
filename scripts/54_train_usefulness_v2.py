from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sklearn.linear_model import LogisticRegression

from plan_b.experiment_utils import build_base_config, summarize_run
from plan_b.io_utils import read_json, write_json, write_jsonl, write_text
from plan_b.mbpp import load_examples
from plan_b.pipeline import run_pipeline
from plan_b.schema import Episode
from retrieval.usefulness_v2 import build_pair_features, retrieve


def build_training_rows(structure_run_path: str, baseline_run_path: str) -> list[dict]:
    structure_run = read_json(structure_run_path)
    baseline_run = read_json(baseline_run_path)
    baseline_by_id = {row["episode"]["query_id"]: row for row in baseline_run["episodes"]}
    rows = []
    for row in structure_run["episodes"]:
        query_id = row["episode"]["query_id"]
        base_row = baseline_by_id[query_id]
        supports = row["episode"]["support_ids"]
        retrieval_scores = row.get("retrieval_scores", [])
        fidelity = float(row.get("structure_fidelity", 0.0))
        label = None
        if row["passed"] and not base_row["passed"]:
            label = 1
        elif base_row["passed"] and not row["passed"]:
            label = 0
        elif fidelity < 0.15:
            label = 0
        elif fidelity >= 0.5 and row["passed"]:
            label = 1
        if label is None:
            continue
        for rank, (support_id, score) in enumerate(zip(supports, retrieval_scores), start=1):
            rows.append(
                {
                    "query_id": query_id,
                    "support_id": support_id,
                    "base_score": float(score),
                    "support_rank": rank,
                    "label": label,
                    "structure_fidelity": fidelity,
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Train usefulness v2 and optionally evaluate on MBPP+100.")
    parser.add_argument("--structure-run", required=True)
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--train-examples", default="data/processed/mbpp/train.jsonl")
    parser.add_argument("--eval-examples", default="data/processed/evalplus/mbppplus_test.jsonl")
    parser.add_argument("--shot", type=int, default=1)
    parser.add_argument("--limit-eval", type=int, default=100)
    parser.add_argument("--candidate-budget", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--pairs-out", default="data/b_support_pairs_v2.jsonl")
    parser.add_argument("--model-out", default="models/b_support_usefulness_v2.json")
    parser.add_argument("--episodes-out", default="data/episodes/mbppplus_test100_usefulness_v2_episodes.jsonl")
    parser.add_argument("--result-out", default="results/mbppplus100_usefulness_v2_multi_prior_mbrexec_budget8_seed1.json")
    parser.add_argument("--report-out", default="paper/b_week3_usefulness_v2.md")
    parser.add_argument("--skip-eval", action="store_true")
    args = parser.parse_args()

    train_examples = load_examples(args.train_examples)
    eval_examples = load_examples(args.eval_examples)[: args.limit_eval]
    train_index = {example.task_id: example for example in train_examples}
    eval_index = {example.task_id: example for example in eval_examples}

    rows = build_training_rows(args.structure_run, args.baseline_run)
    write_jsonl(args.pairs_out, rows)

    features = []
    labels = []
    for row in rows:
        query = eval_index.get(row["query_id"])
        support = train_index.get(row["support_id"])
        if query is None or support is None:
            continue
        features.append(build_pair_features(query, support, row["base_score"]))
        labels.append(int(row["label"]))

    model = LogisticRegression(max_iter=500, class_weight="balanced", random_state=1)
    model.fit(features, labels)
    payload = {
        "weights": model.coef_[0].tolist(),
        "bias": float(model.intercept_[0]),
        "num_pairs": len(features),
        "positive_rate": sum(labels) / max(len(labels), 1),
        "feature_dim": len(features[0]) if features else 0,
    }
    write_json(args.model_out, payload)

    episode_rows = []
    for query in eval_examples:
        supports = retrieve(query, train_examples, top_k=args.shot, weights=payload["weights"], bias=payload["bias"])
        episode_rows.append(
            Episode(
                episode_id=f"{query.task_id}_k{args.shot}_usefulness_v2",
                query_id=query.task_id,
                k=args.shot,
                retrieval_mode="usefulness_v2",
                support_ids=[support.task_id for _, support in supports],
                query_prompt=query.prompt,
                tests_path="",
                entry_point=query.entry_point,
            ).to_dict()
        )
    write_jsonl(args.episodes_out, episode_rows)

    report_lines = [
        "# Week3 Usefulness V2",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| num_pairs | {payload['num_pairs']} |",
        f"| positive_rate | {payload['positive_rate']:.4f} |",
        f"| feature_dim | {payload['feature_dim']} |",
    ]

    if not args.skip_eval:
        config = build_base_config("mbppplus100", "usefulness_v2", args.candidate_budget, seed=args.seed)
        config.update(
            {
                "episodes_path": args.episodes_out,
                "prior_mode": "multi_candidate",
                "gate_mode": "none",
                "rerank_mode": "mbr_exec",
                "num_prior_candidates": 2,
                "result_path": args.result_out,
                "max_episodes": args.limit_eval,
            }
        )
        result = run_pipeline(config)
        write_json(args.result_out, result)
        summary = summarize_run(result)
        baseline = read_json(args.structure_run)
        baseline_passed = sum(1 for row in baseline["episodes"][: args.limit_eval] if row.get("passed"))
        summary["delta_vs_structure_run"] = summary["passed"] - baseline_passed
        report_lines.extend(
            [
                "",
                "| Eval Metric | Value |",
                "| --- | ---: |",
                f"| passed | {summary['passed']}/{summary['num_episodes']} |",
                f"| pass_rate | {summary['pass_rate']:.4f} |",
                f"| delta_vs_structure_run | {summary['delta_vs_structure_run']:+d} |",
                f"| avg_candidates | {summary['avg_candidates_per_episode']:.2f} |",
            ]
        )

    write_text(args.report_out, "\n".join(report_lines) + "\n")


if __name__ == "__main__":
    main()
