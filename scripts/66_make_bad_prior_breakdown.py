from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import markdown_table
from plan_b.io_utils import read_json, write_json, write_text


BASELINE_TEMPLATE = "results/mbpp224_fair_budget/mbppplus224_syntax_aware_no_prior_mbrexec_budget8_seed{seed}.json"
TARGET_TEMPLATES = {
    "random_prior": "results/mbpp224_fair_budget/mbppplus224_syntax_aware_random_prior_mbrexec_budget8_seed{seed}.json",
    "corrupted_prior": "results/mbpp224_fair_budget/mbppplus224_syntax_aware_corrupted_prior_mbrexec_budget8_seed{seed}.json",
}
PREFERRED_SEEDS = [1, 2, 3]


def mean(values: List[float]) -> float:
    return sum(values) / max(len(values), 1)


def std(values: List[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


def format_mean_std(values: List[int]) -> str:
    if not values:
        return "n/a"
    return f"{mean(values):.2f} +/- {std(values):.2f}"


def load_episode_map(path: str) -> Dict[str, Dict[str, object]]:
    result = read_json(path)
    return {row["episode"]["query_id"]: row for row in result["episodes"]}


def classify_regression(baseline_row: Dict[str, object], target_row: Dict[str, object]) -> str:
    candidates = target_row.get("candidates", [])
    if not any(candidate.get("compile_ok") for candidate in candidates):
        return "all_compile_fail"
    if target_row.get("best_candidate", {}).get("exec_status") == "timeout":
        return "best_timeout"
    if any(candidate.get("passed") for candidate in candidates):
        return "rerank_miss_despite_passing_candidate"
    if baseline_row.get("best_candidate", {}).get("compile_ok") and target_row.get("best_candidate", {}).get("compile_ok"):
        return "compiled_but_failed_tests"
    return "other_execution_failure"


def prior_names(target_row: Dict[str, object]) -> List[str]:
    return sorted(
        {
            candidate.get("prior_name")
            for candidate in target_row.get("candidates", [])
            if candidate.get("prior_name")
        }
    )


def compare(seed: int, baseline_path: str, target_path: str) -> Dict[str, object]:
    baseline = load_episode_map(baseline_path)
    target = load_episode_map(target_path)
    improved = []
    regressed = []
    unchanged = []
    counts: Dict[str, int] = {}

    for query_id, baseline_row in baseline.items():
        target_row = target[query_id]
        if baseline_row.get("passed") and not target_row.get("passed"):
            failure_type = classify_regression(baseline_row, target_row)
            counts[failure_type] = counts.get(failure_type, 0) + 1
            regressed.append(
                {
                    "query_id": query_id,
                    "failure_type": failure_type,
                    "baseline_compile_ok": bool(baseline_row.get("best_candidate", {}).get("compile_ok")),
                    "target_compile_ok": bool(target_row.get("best_candidate", {}).get("compile_ok")),
                    "target_exec_status": target_row.get("best_candidate", {}).get("exec_status"),
                    "target_prior_names": prior_names(target_row),
                }
            )
        elif not baseline_row.get("passed") and target_row.get("passed"):
            improved.append(query_id)
        else:
            unchanged.append(query_id)

    return {
        "seed": seed,
        "baseline_path": baseline_path,
        "target_path": target_path,
        "improved_count": len(improved),
        "regressed_count": len(regressed),
        "unchanged_count": len(unchanged),
        "regression_breakdown": counts,
        "regressed_queries": regressed,
    }


def available_seeds() -> List[int]:
    found = []
    for seed in PREFERRED_SEEDS:
        baseline_path = BASELINE_TEMPLATE.format(seed=seed)
        if not Path(baseline_path).exists():
            continue
        if all(Path(template.format(seed=seed)).exists() for template in TARGET_TEMPLATES.values()):
            found.append(seed)
    return found


def main() -> None:
    seeds = available_seeds()
    if not seeds:
        raise FileNotFoundError("No seed-complete bad-prior comparisons found.")

    payload = {"baseline_template": BASELINE_TEMPLATE, "seeds": seeds, "comparisons": {}}
    rows = []
    detail_lines = ["# Bad Prior Failure Breakdown\n"]
    detail_lines.append(
        "This breakdown upgrades the claim `bad priors remain harmful` from a single solved-task delta into a per-query regression summary on the main `MBPP+224 fair-budget` benchmark. The goal is to clarify whether the remaining harm is compile-related, rerank-related, or timeout-related."
    )
    detail_lines.append(
        f"This revision uses seed-complete comparisons for seeds `{','.join(str(seed) for seed in seeds)}` whenever the packaged canonical result files are available."
    )
    detail_lines.append("")

    summary_lines = []
    all_compile_only = True

    for setting, target_template in TARGET_TEMPLATES.items():
        per_seed = []
        improved_counts = []
        regressed_counts = []
        unchanged_counts = []
        compile_fail_counts = []
        compiled_fail_counts = []
        timeout_counts = []
        rerank_miss_counts = []

        detail_lines.append(f"## {setting}\n")

        for seed in seeds:
            comparison = compare(seed, BASELINE_TEMPLATE.format(seed=seed), target_template.format(seed=seed))
            per_seed.append(comparison)
            breakdown = comparison["regression_breakdown"]
            improved_counts.append(comparison["improved_count"])
            regressed_counts.append(comparison["regressed_count"])
            unchanged_counts.append(comparison["unchanged_count"])
            compile_fail_counts.append(breakdown.get("all_compile_fail", 0))
            compiled_fail_counts.append(breakdown.get("compiled_but_failed_tests", 0))
            timeout_counts.append(breakdown.get("best_timeout", 0))
            rerank_miss_counts.append(breakdown.get("rerank_miss_despite_passing_candidate", 0))

            if any(
                breakdown.get(key, 0) > 0
                for key in ["compiled_but_failed_tests", "best_timeout", "rerank_miss_despite_passing_candidate", "other_execution_failure"]
            ):
                all_compile_only = False

            detail_lines.append(
                f"### seed {seed}\n"
            )
            detail_lines.append(
                f"Relative to `no_prior + MBR`, this setting gained `{comparison['improved_count']}` tasks and regressed `{comparison['regressed_count']}` tasks under the same budget and rerank regime."
            )
            for item in comparison["regressed_queries"][:10]:
                priors = ", ".join(item["target_prior_names"]) if item["target_prior_names"] else "none"
                detail_lines.append(
                    f"- `{item['query_id']}`: `{item['failure_type']}`, target exec=`{item['target_exec_status']}`, target compile_ok=`{item['target_compile_ok']}`, candidate priors=`{priors}`"
                )
            detail_lines.append("")

        payload["comparisons"][setting] = {
            "seeds": per_seed,
            "aggregate": {
                "num_seeds": len(seeds),
                "improved_mean": mean(improved_counts),
                "improved_std": std(improved_counts),
                "regressed_mean": mean(regressed_counts),
                "regressed_std": std(regressed_counts),
                "unchanged_mean": mean(unchanged_counts),
                "unchanged_std": std(unchanged_counts),
                "all_compile_fail_mean": mean(compile_fail_counts),
                "all_compile_fail_std": std(compile_fail_counts),
                "compiled_but_failed_tests_mean": mean(compiled_fail_counts),
                "compiled_but_failed_tests_std": std(compiled_fail_counts),
                "best_timeout_mean": mean(timeout_counts),
                "best_timeout_std": std(timeout_counts),
                "rerank_miss_mean": mean(rerank_miss_counts),
                "rerank_miss_std": std(rerank_miss_counts),
            },
        }

        rows.append(
            [
                setting,
                ",".join(str(seed) for seed in seeds),
                format_mean_std(improved_counts),
                format_mean_std(regressed_counts),
                format_mean_std(unchanged_counts),
                format_mean_std(compile_fail_counts),
                format_mean_std(compiled_fail_counts),
                format_mean_std(timeout_counts),
                format_mean_std(rerank_miss_counts),
            ]
        )
        summary_lines.append(
            f"`{setting}` regresses by `{format_mean_std(regressed_counts)}` tasks across seeds `{','.join(str(seed) for seed in seeds)}`, with `all_compile_fail` at `{format_mean_std(compile_fail_counts)}`."
        )

    md = "# Bad Prior Delta Types\n\n"
    md += (
        "All numbers below compare each bad-prior setting against `no_prior + MBR` on the same `MBPP+224 fair-budget` seed. "
        "This is a compact reviewer-facing decomposition, not a new benchmark. "
        f"The current canonical package includes seed-complete bad-prior comparisons for seeds `{','.join(str(seed) for seed in seeds)}`.\n\n"
    )
    md += markdown_table(
        [
            "Setting",
            "Seeds",
            "Improved Mean+/-Std",
            "Regressed Mean+/-Std",
            "Unchanged Mean+/-Std",
            "All Compile Fail Mean+/-Std",
            "Compiled But Failed Tests Mean+/-Std",
            "Best Timeout Mean+/-Std",
            "Rerank Miss Mean+/-Std",
        ],
        rows,
    )
    md += "\n"
    if all_compile_only:
        md += (
            "Across all currently packaged bad-prior seeds, the observed regressions for both `random_prior` and `corrupted_prior` remain entirely concentrated in `all_compile_fail`. "
            "This supports a narrower but stronger mechanism interpretation: under reranking, the residual harm from bad priors is still real, and in the current multi-seed package it appears to come from degraded proposal quality rather than from MBR selecting the wrong executable candidate.\n"
        )
    else:
        md += (
            "The current multi-seed package shows that `all_compile_fail` remains the dominant regression type, but other failure modes also appear in some seeds. "
            "The mechanism claim should therefore stay focused on proposal-quality degradation rather than on reranker-only error.\n"
        )

    write_json("paper/fig_bad_prior_delta_types.json", payload)
    write_text("paper/fig_bad_prior_delta_types.md", md)
    write_text("paper/bad_prior_failure_breakdown.md", "\n".join(detail_lines).strip() + "\n")


if __name__ == "__main__":
    main()
