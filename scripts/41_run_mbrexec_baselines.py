from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import build_base_config, markdown_table, summarize_run
from plan_b.io_utils import write_json, write_text
from plan_b.pipeline import run_pipeline


SETTING_OVERRIDES = {
    "no_prior_nombr": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "none", "num_prior_candidates": 0},
    "no_prior_mbrexec": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "single_prior_nombr": {"prior_mode": "single", "gate_mode": "none", "rerank_mode": "none", "num_prior_candidates": 1},
    "single_prior_mbrexec": {"prior_mode": "single", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "random_prior_mbrexec": {"prior_mode": "random", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "corrupted_prior_mbrexec": {"prior_mode": "corrupted", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "weak_prior_nombr": {"prior_mode": "weak", "gate_mode": "none", "rerank_mode": "none", "num_prior_candidates": 1},
    "weak_prior_mbrexec": {"prior_mode": "weak", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "multi_prior_nombr": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "none", "num_prior_candidates": 2},
    "multi_prior_mbrexec": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
    "multi_prior_threshold_mbrexec": {"prior_mode": "multi_candidate", "gate_mode": "threshold", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
}


def sanitize_name(name: str) -> str:
    return name.replace("+", "_plus_").replace("/", "_").replace("-", "_")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fixed-budget MBR baselines for Plan B.")
    parser.add_argument("--dataset", default="mbppplus100")
    parser.add_argument("--retrieval", default="syntax_aware")
    parser.add_argument("--candidate-budget", type=int, default=8)
    parser.add_argument("--settings", nargs="+", required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", default="results/b_week1_key_baselines.json")
    parser.add_argument("--paper-out", default="paper/b_week1_key_baselines.md")
    args = parser.parse_args()

    payload = {
        "dataset": args.dataset,
        "retrieval": args.retrieval,
        "candidate_budget": args.candidate_budget,
        "seed": args.seed,
        "settings": {},
    }
    table_rows = []
    for setting in args.settings:
        if setting not in SETTING_OVERRIDES:
            raise ValueError(f"Unknown setting: {setting}")
        config = build_base_config(args.dataset, args.retrieval, args.candidate_budget, seed=args.seed)
        config.update(SETTING_OVERRIDES[setting])
        result_path = f"results/{args.dataset}_{args.retrieval}_{sanitize_name(setting)}_budget{args.candidate_budget}_seed{args.seed}.json"
        config["result_path"] = result_path
        result = run_pipeline(config)
        write_json(result_path, result)
        summary = summarize_run(result)
        summary["result_path"] = result_path
        payload["settings"][setting] = summary
        table_rows.append(
            [
                setting,
                f"{summary['pass_rate']:.4f}",
                f"{summary['passed']}/{summary['num_episodes']}",
                f"{summary['compile_ok']}/{summary['num_episodes']}",
                summary["failed"],
                summary["timeout"],
                f"{summary['avg_candidates_per_episode']:.2f}",
            ]
        )
    write_json(args.out, payload)
    md = "# Week1 Key Baselines\n\n"
    md += markdown_table(
        ["Setting", "Pass Rate", "Passed", "Compile OK", "Failed", "Timeout", "Avg Candidates"],
        table_rows,
    )
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
