from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Dict, List, Sequence

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text


SETTINGS = ["no_prior", "single_prior", "multi_prior"]


def parse_csv_ints(raw: str) -> List[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def mean(values: Sequence[float]) -> float:
    return sum(values) / max(len(values), 1)


def std(values: Sequence[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


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
    parser = argparse.ArgumentParser(description="Aggregate the budget sweep across multiple seeds with uncertainty bars.")
    parser.add_argument("--dataset", default="mbppplus100")
    parser.add_argument("--budgets", default="1,4,8,16")
    parser.add_argument("--seeds", default="1,2")
    parser.add_argument("--out", default="paper/fig_budget_sweep_v2.json")
    parser.add_argument("--paper-out", default="paper/fig_budget_sweep_v2.md")
    args = parser.parse_args()

    budgets = parse_csv_ints(args.budgets)
    seeds = parse_csv_ints(args.seeds)
    payload: Dict[str, object] = {"dataset": args.dataset, "budgets": {}, "seeds": seeds, "missing": []}
    rows = []

    for budget in budgets:
        budget_payload: Dict[str, object] = {}
        for setting in SETTINGS:
            runs = []
            missing = []
            for seed in seeds:
                result_path = find_result_path(args.dataset, setting, budget, seed)
                if result_path is None:
                    missing.append(seed)
                    continue
                summary = summarize_run(read_json(result_path))
                runs.append({"seed": seed, "result_path": str(result_path), "summary": summary})

            if not runs:
                payload["missing"].append({"budget": budget, "setting": setting, "missing_seeds": missing})
                rows.append([budget, setting, "missing", "missing", "-", "-"])
                continue

            solved = [run["summary"]["passed"] for run in runs]
            pass_rates = [run["summary"]["pass_rate"] for run in runs]
            budget_payload[setting] = {
                "runs": runs,
                "solved_mean": mean(solved),
                "solved_std": std(solved),
                "pass_rate_mean": mean(pass_rates),
                "pass_rate_std": std(pass_rates),
                "available_seeds": [run["seed"] for run in runs],
                "missing_seeds": missing,
            }
            rows.append(
                [
                    budget,
                    setting,
                    f"{mean(solved):.2f} +/- {std(solved):.2f}",
                    f"{mean(pass_rates):.4f} +/- {std(pass_rates):.4f}",
                    ",".join(str(run["seed"]) for run in runs),
                    ",".join(str(seed) for seed in missing) if missing else "-",
                ]
            )
        payload["budgets"][str(budget)] = budget_payload

    md = "# Budget Sweep V2\n\n"
    md += "This version aggregates the key budget-sweep points across multiple seeds so the E&D figure is not read as a single-seed anecdote. It should be described as mechanism support on `MBPP+100`, not as a headline benchmark claim.\n\n"
    md += markdown_table(
        ["Budget", "Setting", "Solved Mean+/-Std", "Pass Rate Mean+/-Std", "Available Seeds", "Missing Seeds"],
        rows,
    )
    md += "\n"
    md += "Caption guidance: every plotted point should state the exact available seeds shown in the `Available Seeds` column. "
    md += "The artifact version of this figure is only claim-valid when read with those per-budget seed counts.\n"
    if payload["missing"]:
        md += "\n## Missing Cells\n\n"
        for item in payload["missing"]:
            seeds_text = ", ".join(str(seed) for seed in item["missing_seeds"])
            md += f"- budget `{item['budget']}` / setting `{item['setting']}` missing seeds `{seeds_text}`\n"

    write_json(args.out, payload)
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
