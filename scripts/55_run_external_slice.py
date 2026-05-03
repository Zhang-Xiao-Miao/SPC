from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import build_base_config, markdown_table, summarize_run
from plan_b.io_utils import write_json, write_jsonl, write_text
from plan_b.mbpp import load_examples
from plan_b.pipeline import run_pipeline
from plan_b.schema import Episode
from retrieval import syntax_aware


SETTING_MAP = {
    "no_prior": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "single_prior": {"prior_mode": "single", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "multi_prior": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
}


DATASET_TO_EPISODES = {
    "humanevalplus20": "data/episodes/humanevalplus_test20_episodes.jsonl",
    "humanevalplus50": "data/episodes/humanevalplus_test50_syntax_episodes.jsonl",
    "humanevalplus164": "data/episodes/humanevalplus_test164_syntax_episodes.jsonl",
}


def ensure_external_episodes(train_path: str, eval_path: str, output_path: str, shot: int, limit: int | None = None) -> None:
    target = Path(output_path)
    if target.exists():
        return
    train_examples = load_examples(train_path)
    eval_examples = load_examples(eval_path)
    if limit is not None:
        eval_examples = eval_examples[:limit]
    rows = []
    for query in eval_examples:
        supports = syntax_aware.retrieve(query, train_examples, max(shot, 1))
        rows.append(
            Episode(
                episode_id=f"{query.task_id}_k{shot}_syntax_aware",
                query_id=query.task_id,
                k=shot,
                retrieval_mode="syntax_aware",
                support_ids=[example.task_id for _, example in supports[:shot]],
                query_prompt=query.prompt,
                tests_path="",
                entry_point=query.entry_point,
            ).to_dict()
        )
    write_jsonl(target, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an external fixed-budget Plan B evaluation slice.")
    parser.add_argument("--dataset", default="humanevalplus50", choices=sorted(DATASET_TO_EPISODES))
    parser.add_argument("--settings", default="no_prior,single_prior,multi_prior")
    parser.add_argument("--candidate-budget", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--generator-backend", default=None)
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--result-prefix", default=None)
    parser.add_argument("--out", default="results/external_slice_humanevalplus50_seed1.json")
    parser.add_argument("--paper-out", default="paper/b_external_slice_humanevalplus50_seed1.md")
    args = parser.parse_args()

    if args.dataset == "humanevalplus50":
        ensure_external_episodes(
            train_path="data/processed/mbpp/train.jsonl",
            eval_path="data/processed/evalplus/humanevalplus_test.jsonl",
            output_path=DATASET_TO_EPISODES[args.dataset],
            shot=1,
            limit=50,
        )
    elif args.dataset == "humanevalplus20":
        ensure_external_episodes(
            train_path="data/processed/mbpp/train.jsonl",
            eval_path="data/processed/evalplus/humanevalplus_test.jsonl",
            output_path=DATASET_TO_EPISODES[args.dataset],
            shot=1,
            limit=20,
        )

    rows = []
    result_prefix = args.result_prefix or args.dataset
    payload = {
        "dataset": args.dataset,
        "candidate_budget": args.candidate_budget,
        "seed": args.seed,
        "generator_backend": args.generator_backend,
        "model_name": args.model_name,
        "settings": {},
        "note": "Using locally available HumanEval+ slice as external fallback because LiveCodeBench/BigCodeBench data are not present in the workspace.",
    }
    for setting in [item.strip() for item in args.settings.split(",") if item.strip()]:
        if setting not in SETTING_MAP:
            raise ValueError(f"Unknown setting: {setting}")
        config = build_base_config(args.dataset, "syntax_aware", args.candidate_budget, seed=args.seed)
        if args.generator_backend:
            config["generator_backend"] = args.generator_backend
        if args.model_name:
            config["model_name"] = args.model_name
        if args.api_base:
            config["api_base"] = args.api_base
        config.update(SETTING_MAP[setting])
        config["episodes_path"] = DATASET_TO_EPISODES[args.dataset]
        result_path = f"results/{result_prefix}_syntax_aware_{setting}_mbrexec_budget{args.candidate_budget}_seed{args.seed}.json"
        config["result_path"] = result_path
        result = run_pipeline(config)
        write_json(result_path, result)
        summary = summarize_run(result)
        summary["result_path"] = result_path
        payload["settings"][setting] = summary
        rows.append(
            [
                setting,
                f"{summary['pass_rate']:.4f}",
                f"{summary['passed']}/{summary['num_episodes']}",
                f"{summary['avg_latency_sec']:.2f}",
                f"{summary['avg_candidates_per_episode']:.2f}",
            ]
        )
    write_json(args.out, payload)
    md = "# External Slice\n\n"
    md += f"- Dataset: `{args.dataset}`\n"
    md += f"- Candidate Budget: `{args.candidate_budget}`\n"
    md += f"- Seed: `{args.seed}`\n"
    md += "- Note: using a local HumanEval+ slice fallback because newer external benchmarks are not available in the workspace.\n\n"
    md += markdown_table(["Setting", "Pass Rate", "Passed", "Avg Latency", "Avg Candidates"], rows)
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
