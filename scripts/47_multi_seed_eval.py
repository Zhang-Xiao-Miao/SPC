from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import build_base_config, markdown_table, summarize_run
from plan_b.io_utils import write_json, write_text
from plan_b.pipeline import run_pipeline


SETTING_MAP = {
    "no_prior_mbrexec": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "single_prior_mbrexec": {"prior_mode": "single", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "multi_prior_mbrexec": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
}


def mean(values):
    return sum(values) / max(len(values), 1)


def std(values):
    if len(values) <= 1:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-seed Plan B evaluation.")
    parser.add_argument("--dataset", default="mbppplus224")
    parser.add_argument("--retrieval", default="syntax_aware")
    parser.add_argument("--settings", nargs="+", default=["no_prior_mbrexec", "multi_prior_mbrexec"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--candidate-budget", type=int, default=8)
    parser.add_argument("--out", default="results/b_multi_seed_eval.json")
    parser.add_argument("--paper-out", default="paper/b_week2_budget_cost_table.md")
    args = parser.parse_args()

    payload = {"dataset": args.dataset, "settings": {}}
    rows = []
    for setting in args.settings:
        run_summaries = []
        for seed in args.seeds:
            config = build_base_config(args.dataset, args.retrieval, args.candidate_budget, seed=seed)
            config.update(SETTING_MAP[setting])
            result_path = f"results/{args.dataset}_{args.retrieval}_{setting}_budget{args.candidate_budget}_seed{seed}.json"
            config["result_path"] = result_path
            result = run_pipeline(config)
            write_json(result_path, result)
            run_summaries.append(summarize_run(result))
        pass_rates = [row["pass_rate"] for row in run_summaries]
        latencies = [row["avg_latency_sec"] for row in run_summaries]
        candidates = [row["avg_candidates_per_episode"] for row in run_summaries]
        prompt_tokens = [row["prompt_tokens_total"] for row in run_summaries]
        completion_tokens = [row["completion_tokens_total"] for row in run_summaries]
        payload["settings"][setting] = {
            "pass_rate_mean": mean(pass_rates),
            "pass_rate_std": std(pass_rates),
            "latency_mean": mean(latencies),
            "avg_candidates_mean": mean(candidates),
            "prompt_tokens_mean": mean(prompt_tokens),
            "completion_tokens_mean": mean(completion_tokens),
            "runs": run_summaries,
        }
        rows.append(
            [
                setting,
                f"{mean(pass_rates):.4f} ± {std(pass_rates):.4f}",
                f"{mean(candidates):.2f}",
                f"{mean(latencies):.2f}",
                f"{mean(prompt_tokens):.0f}",
                f"{mean(completion_tokens):.0f}",
            ]
        )
    write_json(args.out, payload)
    md = "# Budget And Cost Profile\n\n"
    md += markdown_table(
        ["Setting", "Pass Rate Mean±Std", "Avg Candidates", "Avg Latency", "Prompt Tokens", "Completion Tokens"],
        rows,
    )
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
