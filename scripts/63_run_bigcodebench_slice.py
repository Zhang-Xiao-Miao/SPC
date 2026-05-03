from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import BASE_GENERATION_CONFIG, markdown_table, summarize_run
from plan_b.io_utils import write_json, write_text
from plan_b.pipeline import run_pipeline


SETTING_MAP = {
    "no_prior": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "multi_prior": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a modern BigCodeBench-Hard compatibility slice for Plan B.")
    parser.add_argument("--settings", default="no_prior,multi_prior")
    parser.add_argument("--candidate-budget", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--generator-backend", default=None)
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--eval-examples", default="data/processed/bigcodebench_hard_compatible20.jsonl")
    parser.add_argument("--episodes", default="data/episodes/bigcodebench_hard_compatible20_syntax_episodes.jsonl")
    parser.add_argument("--slice-tag", default="bigcodebench_hard_compatible20")
    parser.add_argument("--max-episodes", type=int, default=None)
    parser.add_argument("--result-prefix", default=None)
    parser.add_argument("--out", default="results/external_slice_bigcodebench_hard20_seed1.json")
    parser.add_argument("--paper-out", default="paper/tbl_external_modern.md")
    args = parser.parse_args()

    max_episodes = args.max_episodes
    if max_episodes is None:
        max_episodes = sum(1 for _ in Path(args.episodes).open("r", encoding="utf-8"))
    result_prefix = args.result_prefix or args.slice_tag

    rows = []
    payload = {
        "dataset": args.slice_tag,
        "candidate_budget": args.candidate_budget,
        "seed": args.seed,
        "generator_backend": args.generator_backend or BASE_GENERATION_CONFIG.get("generator_backend"),
        "model_name": args.model_name or BASE_GENERATION_CONFIG.get("model_name"),
        "settings": {},
        "note": "Compatibility-filtered BigCodeBench-Hard slice using only tasks whose declared dependency roots are importable in the current environment.",
    }
    settings = [item.strip() for item in args.settings.split(",") if item.strip()]

    for setting in settings:
        config = dict(BASE_GENERATION_CONFIG)
        config.update(
            {
                "dataset": args.slice_tag,
                "train_examples": "data/processed/mbpp/train.jsonl",
                "eval_examples": args.eval_examples,
                "episodes_path": args.episodes,
                "k_support": 1,
                "retrieval_mode": "syntax_aware",
                "max_episodes": max_episodes,
                "candidate_budget": args.candidate_budget,
                "seed": args.seed,
            }
        )
        if args.generator_backend:
            config["generator_backend"] = args.generator_backend
        if args.model_name:
            config["model_name"] = args.model_name
        if args.api_base:
            config["api_base"] = args.api_base
        config.update(SETTING_MAP[setting])
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
    md = "# Modern External Slice\n\n"
    md += f"- Dataset: `BigCodeBench-Hard v0.1.4` compatibility-filtered `{max_episodes}`-task slice\n"
    md += f"- Candidate Budget: `{args.candidate_budget}`\n"
    md += f"- Seed: `{args.seed}`\n"
    md += "- Caveat: this slice is filtered for dependency compatibility with the current environment, so it supports a feasibility check rather than a full-benchmark generalization claim.\n\n"
    md += markdown_table(["Setting", "Pass Rate", "Passed", "Avg Latency", "Avg Candidates"], rows)
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
