from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text


RESULT_TEMPLATE = "results/mbpp224_fair_budget/mbppplus224_syntax_aware_{setting}_mbrexec_budget8_seed{seed}.json"
SEEDS = [1, 2, 3]


def exact_binomial_two_sided(successes: int, trials: int) -> float:
    if trials <= 0:
        return 1.0
    cutoff = math.comb(trials, successes)
    total = 2 ** trials
    numerator = 0
    for k in range(trials + 1):
        if math.comb(trials, k) <= cutoff:
            numerator += math.comb(trials, k)
    return min(1.0, numerator / total)


def load_pass_map(path: str) -> Dict[str, bool]:
    result = read_json(path)
    return {row["episode"]["query_id"]: bool(row["passed"]) for row in result["episodes"]}


def compare_paths(baseline_path: str, target_path: str) -> Dict[str, object]:
    baseline = load_pass_map(baseline_path)
    target = load_pass_map(target_path)
    improved = sorted(query_id for query_id in baseline if not baseline[query_id] and target.get(query_id, False))
    regressed = sorted(query_id for query_id in baseline if baseline[query_id] and not target.get(query_id, False))
    unchanged = sorted(query_id for query_id in baseline if baseline[query_id] == target.get(query_id, False))
    p_value = exact_binomial_two_sided(max(len(improved), len(regressed)), len(improved) + len(regressed))
    return {
        "improved": improved,
        "regressed": regressed,
        "unchanged": unchanged,
        "improved_count": len(improved),
        "regressed_count": len(regressed),
        "unchanged_count": len(unchanged),
        "p_value_sign_test": p_value,
    }


def summarize_setting(path: str) -> Dict[str, object]:
    return summarize_run(read_json(path))


def main() -> None:
    comparisons: List[Dict[str, object]] = []
    stats_rows = []
    cost_rows = []

    for seed in SEEDS:
        baseline_path = RESULT_TEMPLATE.format(setting="no_prior", seed=seed)
        single_path = RESULT_TEMPLATE.format(setting="single_prior", seed=seed)
        multi_path = RESULT_TEMPLATE.format(setting="multi_prior", seed=seed)

        baseline_summary = summarize_setting(baseline_path)
        single_summary = summarize_setting(single_path)
        multi_summary = summarize_setting(multi_path)

        single_cmp = compare_paths(baseline_path, single_path)
        multi_cmp = compare_paths(baseline_path, multi_path)

        comparisons.append(
            {
                "seed": seed,
                "baseline_path": baseline_path,
                "single_prior_path": single_path,
                "multi_prior_path": multi_path,
                "single_prior": single_cmp,
                "multi_prior": multi_cmp,
            }
        )

        stats_rows.append(
            [
                f"seed{seed} single vs no_prior",
                single_cmp["improved_count"],
                single_cmp["regressed_count"],
                single_cmp["unchanged_count"],
                f"{single_cmp['p_value_sign_test']:.4f}",
            ]
        )
        stats_rows.append(
            [
                f"seed{seed} multi vs no_prior",
                multi_cmp["improved_count"],
                multi_cmp["regressed_count"],
                multi_cmp["unchanged_count"],
                f"{multi_cmp['p_value_sign_test']:.4f}",
            ]
        )

        cost_rows.extend(
            [
                [
                    f"seed{seed} no_prior",
                    baseline_summary["passed"],
                    f"{baseline_summary['avg_candidates_per_episode']:.2f}",
                    f"{baseline_summary['avg_latency_sec']:.3f}",
                    baseline_summary["prompt_tokens_total"],
                    baseline_summary["completion_tokens_total"],
                    baseline_summary["candidate_budget_total"],
                ],
                [
                    f"seed{seed} single_prior",
                    single_summary["passed"],
                    f"{single_summary['avg_candidates_per_episode']:.2f}",
                    f"{single_summary['avg_latency_sec']:.3f}",
                    single_summary["prompt_tokens_total"],
                    single_summary["completion_tokens_total"],
                    single_summary["candidate_budget_total"],
                ],
                [
                    f"seed{seed} multi_prior",
                    multi_summary["passed"],
                    f"{multi_summary['avg_candidates_per_episode']:.2f}",
                    f"{multi_summary['avg_latency_sec']:.3f}",
                    multi_summary["prompt_tokens_total"],
                    multi_summary["completion_tokens_total"],
                    multi_summary["candidate_budget_total"],
                ],
            ]
        )

    pooled_improved = sum(item["multi_prior"]["improved_count"] for item in comparisons)
    pooled_regressed = sum(item["multi_prior"]["regressed_count"] for item in comparisons)
    pooled_unchanged = sum(item["multi_prior"]["unchanged_count"] for item in comparisons)
    pooled_p = exact_binomial_two_sided(max(pooled_improved, pooled_regressed), pooled_improved + pooled_regressed)

    payload = {
        "comparisons": comparisons,
        "pooled_multi_vs_no_prior": {
            "improved_count": pooled_improved,
            "regressed_count": pooled_regressed,
            "unchanged_count": pooled_unchanged,
            "p_value_sign_test": pooled_p,
        },
    }

    md = "# Stats And Cost For Fair-Budget MBPP+224\n\n"
    md += "The paired comparison below uses shared-query outcome changes under matched seed and budget. It is intended as a reviewer-facing sanity check, not as a substitute for the main solved-task table.\n\n"
    md += markdown_table(
        ["Comparison", "Improved", "Regressed", "Unchanged", "Two-Sided Sign-Test p"],
        stats_rows,
    )
    md += "\n"
    md += f"Pooled `multi_prior` vs `no_prior` across all three seeds: improved `{pooled_improved}`, regressed `{pooled_regressed}`, unchanged `{pooled_unchanged}`, two-sided sign-test `p={pooled_p:.4f}`.\n\n"
    md += markdown_table(
        [
            "Run",
            "Solved",
            "Avg Candidates",
            "Avg Latency (s)",
            "Prompt Tokens",
            "Completion Tokens",
            "Execution Calls",
        ],
        cost_rows,
    )
    md += "\n"
    md += "All compared settings use the same candidate budget and rerank regime, and the `Execution Calls` column is matched within each compared seed.\n"
    md += "Prompt-token totals are not equal across prior conditions, so the fairness claim should be written as matched candidate budget plus matched execution-call accounting, not as full compute equality.\n"

    write_json("paper/tbl_stats_cost.json", payload)
    write_text("paper/tbl_stats_cost.md", md)


if __name__ == "__main__":
    main()
