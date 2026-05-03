from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text


def main() -> None:
    old_baseline_path = Path("results/mbppplus_full_k1_syntax_noprior_nogate_nombr_vllm_seed1.json")
    old_best_path = Path("results/mbppplus_full_k1_syntax_multiprior_nogate_mbrexec_vllm_seed1.json")
    fair_summary_path = Path("results/mbpp224_fair_budget/summary.json")
    prompt_only_summary_path = Path("results/prompt_only_structural_mbpp224_fair_budget/summary.json")

    old_baseline = summarize_run(read_json(old_baseline_path))
    old_best = summarize_run(read_json(old_best_path))
    fair_summary = read_json(fair_summary_path)
    fair_settings = fair_summary["settings"]

    fair_no_prior = fair_settings["no_prior"]
    fair_multi = fair_settings["multi_prior"]
    fair_random = fair_settings["random_prior"]
    fair_corrupted = fair_settings["corrupted_prior"]
    prompt_only_summary = read_json(prompt_only_summary_path)
    prompt_only_settings = prompt_only_summary["settings"]
    prompt_no_prior = prompt_only_settings["no_prior"]
    prompt_multi = prompt_only_settings["multi_prior"]

    def fmt_mean_std(row: dict) -> str:
        return f"{row['solved_mean']:.2f} +/- {row['solved_std']:.2f}"

    rows = [
        [
            "Earlier / uncontrolled comparison",
            "syntax-aware / no prior / no rerank",
            "syntax-aware / multi prior / always-on / MBR-exec",
            f"{old_baseline['passed']}/224",
            f"{old_best['passed']}/224",
            f"{old_best['passed'] - old_baseline['passed']:+d}",
            "Large absolute gain, but structural conditioning and execution-selection opportunity are entangled.",
        ],
        [
            "Fair-budget diagnostic comparison",
            "no_prior + MBR",
            "multi_prior + MBR",
            fmt_mean_std(fair_no_prior),
            fmt_mean_std(fair_multi),
            f"{fair_multi['delta_vs_no_prior_mean']:+.2f}",
            "Structural priors retain a modest effect in fixed code-aware diagnostic episodes.",
        ],
        [
            "Full prompt-only structural control",
            "no_prior + MBR",
            "multi_prior + MBR",
            fmt_mean_std(prompt_no_prior),
            fmt_mean_std(prompt_multi),
            f"{prompt_multi['delta_vs_no_prior_mean']:+.2f}",
            "Prompt-only structural retrieval does not reproduce the positive main effect on full MBPP+224.",
        ],
        [
            "Fair-budget bad-prior stress test",
            "no_prior + MBR",
            "random / corrupted prior + MBR",
            f"{fair_no_prior['solved_mean']:.2f}",
            f"{fair_random['solved_mean']:.2f} / {fair_corrupted['solved_mean']:.2f}",
            f"{fair_random['delta_vs_no_prior_mean']:+.2f} / {fair_corrupted['delta_vs_no_prior_mean']:+.2f}",
            "Bad priors remain harmful even under the same diagnostic execution-selection protocol.",
        ],
    ]

    payload = {
        "old_pipeline": {
            "baseline_path": str(old_baseline_path),
            "best_path": str(old_best_path),
            "baseline_passed": old_baseline["passed"],
            "best_passed": old_best["passed"],
            "delta_passed": old_best["passed"] - old_baseline["passed"],
        },
        "fair_budget": {
            "summary_path": str(fair_summary_path),
            "no_prior": fair_no_prior,
            "multi_prior": fair_multi,
            "random_prior": fair_random,
            "corrupted_prior": fair_corrupted,
        },
        "prompt_only_structural_full": {
            "summary_path": str(prompt_only_summary_path),
            "no_prior": prompt_no_prior,
            "multi_prior": prompt_multi,
        },
    }

    md = "# Conclusion Shift Under Fair Evaluation\n\n"
    md += "This table is the paper's E&D centerpiece: it shows that changing the evaluation design changes the scientific interpretation of the same method family.\n\n"
    md += markdown_table(
        [
            "Regime",
            "Baseline",
            "Compared Setting",
            "Baseline Solved",
            "Compared Solved",
            "Delta",
            "Interpretation",
        ],
        rows,
    )
    md += "\n"
    md += "Takeaway: the earlier pipeline supported a strong but entangled \"structure helps a lot\" reading. The fair-budget diagnostic protocol supports a more precise E&D claim: structural-prior effects are conditioned by evaluation design, information access, and prior quality.\n"

    write_json("paper/tbl_conclusion_shift.json", payload)
    write_text("paper/tbl_conclusion_shift.md", md)


if __name__ == "__main__":
    main()
