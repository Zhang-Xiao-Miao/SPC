from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sklearn.linear_model import LogisticRegression

from plan_b.io_utils import read_json, write_json, write_jsonl
from plan_b.mbpp import load_examples
from plan_b.schema import Episode
from retrieval import syntax_aware
from retrieval.usefulness_rerank import build_pair_features, retrieve


def build_training_rows(structure_run_path: str, baseline_run_path: str):
    structure_run = read_json(structure_run_path)
    baseline_run = read_json(baseline_run_path)
    baseline_by_id = {row["episode"]["query_id"]: row for row in baseline_run["episodes"]}
    rows = []
    for row in structure_run["episodes"]:
        query_id = row["episode"]["query_id"]
        base_row = baseline_by_id[query_id]
        supports = row["episode"]["support_ids"]
        label = None
        if row["passed"] and not base_row["passed"]:
            label = 1
        elif base_row["passed"] and not row["passed"]:
            label = 0
        elif float(row.get("structure_fidelity", 0.0)) < 0.15:
            label = 0
        if label is None:
            continue
        for support_id, score in zip(supports, row.get("retrieval_scores", [])):
            rows.append({"query_id": query_id, "support_id": support_id, "base_score": float(score), "label": label})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a support usefulness scorer and rebuild episodes.")
    parser.add_argument("--structure-run", required=True)
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--train-examples", default="data/processed/mbpp/train.jsonl")
    parser.add_argument("--eval-examples", default="data/processed/evalplus/mbppplus_test.jsonl")
    parser.add_argument("--shot", type=int, default=1)
    parser.add_argument("--limit-eval", type=int, default=100)
    parser.add_argument("--pairs-out", default="data/b_support_pairs.jsonl")
    parser.add_argument("--model-out", default="models/b_support_usefulness.json")
    parser.add_argument("--episodes-out", default="data/episodes/mbppplus_test100_usefulness_episodes.jsonl")
    parser.add_argument("--report-out", default="paper/b_week4_support_usefulness.md")
    args = parser.parse_args()

    train_examples = load_examples(args.train_examples)
    eval_examples = load_examples(args.eval_examples)[: args.limit_eval]
    train_index = {example.task_id: example for example in train_examples}
    eval_index = {example.task_id: example for example in eval_examples}

    rows = build_training_rows(args.structure_run, args.baseline_run)
    write_jsonl(args.pairs_out, rows)

    x = []
    y = []
    for row in rows:
        query = eval_index[row["query_id"]]
        support = train_index[row["support_id"]]
        x.append(build_pair_features(query, support, row["base_score"]))
        y.append(int(row["label"]))
    model = LogisticRegression(max_iter=500, class_weight="balanced")
    model.fit(x, y)
    payload = {
        "weights": model.coef_[0].tolist(),
        "bias": float(model.intercept_[0]),
        "num_pairs": len(rows),
        "positive_rate": sum(y) / max(len(y), 1),
    }
    write_json(args.model_out, payload)

    episode_rows = []
    for query in eval_examples:
        supports = retrieve(query, train_examples, top_k=args.shot, weights=payload["weights"], bias=payload["bias"])
        episode_rows.append(
            Episode(
                episode_id=f"{query.task_id}_k{args.shot}_usefulness",
                query_id=query.task_id,
                k=args.shot,
                retrieval_mode="usefulness_rerank",
                support_ids=[support.task_id for _, support in supports],
                query_prompt=query.prompt,
                tests_path="",
                entry_point=query.entry_point,
            ).to_dict()
        )
    write_jsonl(args.episodes_out, episode_rows)

    md = "# Week4 Support Usefulness\n\n"
    md += "| Metric | Value |\n| --- | ---: |\n"
    md += f"| num_pairs | {payload['num_pairs']} |\n"
    md += f"| positive_rate | {payload['positive_rate']:.4f} |\n"
    Path(args.report_out).write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
