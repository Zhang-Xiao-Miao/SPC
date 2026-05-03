from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import build_base_config, markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text
from plan_b.pipeline import run_pipeline


SETTING_MAP = {
    "no_prior": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "single_prior": {"prior_mode": "single", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "multi_prior": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
}


def parse_csv_ints(raw: str) -> List[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def parse_csv_list(raw: str) -> List[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def canonical_result_path(dataset: str, setting: str, budget: int, seed: int) -> Path:
    return Path(f"results/budget_sweep/{dataset}_syntax_aware_{setting}_mbrexec_budget{budget}_seed{seed}.json")


def legacy_result_path(dataset: str, setting: str, budget: int, seed: int) -> Path:
    return Path(f"results/{dataset}_syntax_aware_{setting}_mbrexec_budget{budget}_seed{seed}.json")


def find_result_path(dataset: str, setting: str, budget: int, seed: int) -> Path | None:
    for path in [canonical_result_path(dataset, setting, budget, seed), legacy_result_path(dataset, setting, budget, seed)]:
        if path.exists():
            return path
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or summarize the budget sweep requested by the E&D revision memo.")
    parser.add_argument("--dataset", default="mbppplus100")
    parser.add_argument("--budgets", default="1,2,4,8,16")
    parser.add_argument("--settings", default="no_prior,single_prior,multi_prior")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--run-missing", action="store_true")
    parser.add_argument("--out", default="paper/fig_budget_sweep.json")
    parser.add_argument("--paper-out", default="paper/fig_budget_sweep.md")
    args = parser.parse_args()

    budgets = parse_csv_ints(args.budgets)
    settings = parse_csv_list(args.settings)

    rows = []
    payload: Dict[str, object] = {"dataset": args.dataset, "seed": args.seed, "budgets": {}, "missing": []}

    for budget in budgets:
        payload["budgets"][str(budget)] = {}
        for setting in settings:
            result_path = find_result_path(args.dataset, setting, budget, args.seed)
            if result_path is None and args.run_missing:
                config = build_base_config(args.dataset, "syntax_aware", budget, seed=args.seed)
                config.update(SETTING_MAP[setting])
                result_path = canonical_result_path(args.dataset, setting, budget, args.seed)
                config["result_path"] = str(result_path)
                result = run_pipeline(config)
                write_json(result_path, result)
            if result_path is None:
                payload["missing"].append({"budget": budget, "setting": setting})
                rows.append([budget, setting, "missing", "-", "-", "-"])
                continue
            summary = summarize_run(read_json(result_path))
            payload["budgets"][str(budget)][setting] = {"result_path": str(result_path), "summary": summary}
            rows.append(
                [
                    budget,
                    setting,
                    f"{summary['passed']}/{summary['num_episodes']}",
                    f"{summary['pass_rate']:.4f}",
                    f"{summary['avg_latency_sec']:.3f}",
                    f"{summary['avg_candidates_per_episode']:.2f}",
                ]
            )

    md = "# Budget Sweep\n\n"
    md += "This sweep is designed to answer the memo's key E&D question: at what test-time compute budget do structural priors still help after reranking is controlled?\n\n"
    md += markdown_table(
        ["Budget", "Setting", "Solved", "Pass Rate", "Avg Latency (s)", "Avg Candidates"],
        rows,
    )
    if payload["missing"]:
        md += "\n## Missing Runs\n\n"
        md += "The following budget-setting cells are still missing from the workspace and require rerunning on a machine that can reach the local generation backend:\n\n"
        for item in payload["missing"]:
            md += f"- budget `{item['budget']}` / setting `{item['setting']}`\n"

    write_json(args.out, payload)
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
