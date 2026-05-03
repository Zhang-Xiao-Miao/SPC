from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import build_base_config, markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text
from plan_b.pipeline import run_pipeline


SETTING_MAP = {
    "no_prior": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "single_prior": {"prior_mode": "single", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "multi_prior": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
    "random_prior": {"prior_mode": "random", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "corrupted_prior": {"prior_mode": "corrupted", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
}

CORE_SETTINGS = {"no_prior", "single_prior", "multi_prior"}


def parse_csv_list(raw: str) -> List[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_csv_ints(raw: str) -> List[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def mean(values: Sequence[float]) -> float:
    return sum(values) / max(len(values), 1)


def std(values: Sequence[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


def current_source_revision() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL)
            .strip()
        )
    except Exception:
        return "unknown"


def result_file_name(dataset: str, retrieval: str, setting: str, budget: int, seed: int) -> str:
    return f"{dataset}_{retrieval}_{setting}_mbrexec_budget{budget}_seed{seed}.json"


def passed_query_ids(result: Dict[str, object]) -> List[str]:
    solved = []
    for row in result.get("episodes", []):
        if row.get("passed"):
            solved.append(row.get("episode", {}).get("query_id", ""))
    return sorted(query_id for query_id in solved if query_id)


def delta_vs_baseline(setting_passed: Iterable[str], baseline_passed: Iterable[str]) -> Dict[str, object]:
    setting_set = set(setting_passed)
    baseline_set = set(baseline_passed)
    gained = sorted(setting_set - baseline_set)
    lost = sorted(baseline_set - setting_set)
    return {
        "delta_solved": len(gained) - len(lost),
        "gained_queries": gained,
        "lost_queries": lost,
    }


def seeds_for_setting(setting: str, all_seeds: Sequence[int], use_all_seeds_for_all_settings: bool = False) -> List[int]:
    if use_all_seeds_for_all_settings or setting in CORE_SETTINGS:
        return list(all_seeds)
    return [all_seeds[0]]


def build_summary_row(setting: str, stats: Dict[str, object]) -> List[object]:
    return [
        setting,
        f"{stats['pass_rate_mean']:.4f} ± {stats['pass_rate_std']:.4f}",
        f"{stats['solved_mean']:.2f}",
        str(stats["solved_range"]),
        f"{stats['avg_latency_sec_mean']:.2f}",
        f"{stats['avg_candidates_mean']:.2f}",
        f"{stats['prompt_tokens_mean']:.0f}",
        f"{stats['completion_tokens_mean']:.0f}",
        f"{stats['delta_vs_no_prior_mean']:+.2f}",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full MBPP+224 fair-budget main table for Plan B.")
    parser.add_argument("--dataset", default="mbppplus224")
    parser.add_argument("--retrieval", default="syntax_aware")
    parser.add_argument(
        "--settings",
        default="no_prior,single_prior,multi_prior,random_prior,corrupted_prior",
        help="Comma-separated settings to run.",
    )
    parser.add_argument("--budget", type=int, default=8)
    parser.add_argument("--seeds", default="1,2,3", help="Comma-separated seeds for core settings.")
    parser.add_argument(
        "--all-settings-use-all-seeds",
        action="store_true",
        help="Apply the full seed list to non-core settings such as random_prior and corrupted_prior.",
    )
    parser.add_argument("--max-episodes", type=int, default=0, help="Optional cap for smoke runs.")
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Reuse an existing result file instead of rerunning the pipeline when the expected path already exists.",
    )
    parser.add_argument("--generator-backend", default=None)
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument("--episodes-path", default=None, help="Optional override for the preset episode file.")
    parser.add_argument("--out", default="results/mbpp224_fair_budget/summary.json")
    parser.add_argument("--paper-out", default="paper/b_mbpp224_fair_budget.md")
    args = parser.parse_args()

    settings = parse_csv_list(args.settings)
    seeds = parse_csv_ints(args.seeds)
    if not seeds:
        raise ValueError("At least one seed is required.")
    unknown = [setting for setting in settings if setting not in SETTING_MAP]
    if unknown:
        raise ValueError(f"Unknown settings: {', '.join(unknown)}")

    out_path = Path(args.out)
    out_dir = out_path.parent
    source_revision = current_source_revision()
    payload: Dict[str, object] = {
        "dataset": args.dataset,
        "retrieval": args.retrieval,
        "candidate_budget": args.budget,
        "execution_budget": args.budget,
        "rerank_mode": "mbr_exec",
        "source_revision": source_revision,
        "settings": {},
    }

    baseline_seed_passed: Dict[int, List[str]] = {}
    for setting in settings:
        for seed in seeds_for_setting(setting, seeds, use_all_seeds_for_all_settings=args.all_settings_use_all_seeds):
            config = build_base_config(args.dataset, args.retrieval, args.budget, seed=seed)
            config.update(SETTING_MAP[setting])
            if args.episodes_path:
                config["episodes_path"] = args.episodes_path
            if args.max_episodes:
                config["max_episodes"] = args.max_episodes
            if args.generator_backend:
                config["generator_backend"] = args.generator_backend
            if args.model_name:
                config["model_name"] = args.model_name
            if args.api_base:
                config["api_base"] = args.api_base
            if args.device:
                config["device"] = args.device
            config["result_path"] = str(out_dir / result_file_name(args.dataset, args.retrieval, setting, args.budget, seed))
            result_path = Path(config["result_path"])
            if args.reuse_existing and result_path.exists():
                result = read_json(result_path)
            else:
                result = run_pipeline(config)
                write_json(config["result_path"], result)
            if setting == "no_prior":
                baseline_seed_passed[seed] = passed_query_ids(result)

    rows = []
    for setting in settings:
        run_records = []
        for seed in seeds_for_setting(setting, seeds, use_all_seeds_for_all_settings=args.all_settings_use_all_seeds):
            result_path = out_dir / result_file_name(args.dataset, args.retrieval, setting, args.budget, seed)
            result = read_json(result_path)
            summary = summarize_run(result)
            # Keep raw solved-task deltas for later failure analysis.
            passed_ids = passed_query_ids(result)
            delta = delta_vs_baseline(passed_ids, baseline_seed_passed.get(seed, []))
            run_records.append(
                {
                    "seed": seed,
                    "result_path": str(result_path),
                    "summary": summary,
                    "passed_query_ids": passed_ids,
                    "delta_vs_no_prior": delta,
                }
            )

        solved_counts = [record["summary"]["passed"] for record in run_records]
        pass_rates = [record["summary"]["pass_rate"] for record in run_records]
        avg_latency = [record["summary"]["avg_latency_sec"] for record in run_records]
        avg_candidates = [record["summary"]["avg_candidates_per_episode"] for record in run_records]
        prompt_tokens = [record["summary"]["prompt_tokens_total"] for record in run_records]
        completion_tokens = [record["summary"]["completion_tokens_total"] for record in run_records]
        deltas = [record["delta_vs_no_prior"]["delta_solved"] for record in run_records]
        aggregate = {
            "num_runs": len(run_records),
            "pass_rate_mean": mean(pass_rates),
            "pass_rate_std": std(pass_rates),
            "solved_mean": mean(solved_counts),
            "solved_std": std(solved_counts),
            "solved_range": [min(solved_counts), max(solved_counts)],
            "avg_latency_sec_mean": mean(avg_latency),
            "avg_candidates_mean": mean(avg_candidates),
            "prompt_tokens_mean": mean(prompt_tokens),
            "completion_tokens_mean": mean(completion_tokens),
            "delta_vs_no_prior_mean": mean(deltas),
            "delta_vs_no_prior_std": std(deltas),
            "runs": run_records,
        }
        payload["settings"][setting] = aggregate
        rows.append(build_summary_row(setting, aggregate))

    write_json(out_path, payload)

    md = f"# {args.dataset} {args.retrieval} Fair-Budget Summary\n\n"
    md += f"- Dataset: `{args.dataset}`\n"
    md += f"- Retrieval: `{args.retrieval}`\n"
    md += f"- Candidate Budget: `{args.budget}`\n"
    md += f"- Execution Budget: `{args.budget}`\n"
    md += f"- Rerank: `mbr_exec`\n"
    md += f"- Source revision: `{source_revision}`\n\n"
    md += markdown_table(
        [
            "Setting",
            "Pass Rate Mean±Std",
            "Solved Mean",
            "Solved Range",
            "Avg Latency",
            "Avg Candidates",
            "Prompt Tokens",
            "Completion Tokens",
            "Delta vs no_prior",
        ],
        rows,
    )
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
