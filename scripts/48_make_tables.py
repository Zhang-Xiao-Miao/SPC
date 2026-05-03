from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import markdown_table
from plan_b.io_utils import read_json, write_text


def maybe_load(path: str):
    target = Path(path)
    if not target.exists():
        return None
    return read_json(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile Plan B next-phase tables.")
    parser.add_argument("--week1", default="results/b_week1_key_baselines.json")
    parser.add_argument("--budget", default="results/b_multi_seed_eval.json")
    parser.add_argument("--selector", default="models/b_action_selector_xgb.json")
    parser.add_argument("--humaneval", default="results/b_humaneval_full.json")
    parser.add_argument("--out-main", default="paper/b_main_tables.md")
    parser.add_argument("--out-claims", default="paper/b_claim_matrix.md")
    args = parser.parse_args()

    week1 = maybe_load(args.week1)
    budget = maybe_load(args.budget)
    selector = maybe_load(args.selector)
    humaneval = maybe_load(args.humaneval)

    sections = ["# B Main Tables", ""]
    if week1:
        rows = []
        for setting, summary in week1["settings"].items():
            rows.append([setting, f"{summary['pass_rate']:.4f}", f"{summary['passed']}/{summary['num_episodes']}", f"{summary['avg_candidates_per_episode']:.2f}"])
        sections.append("## Week1 Key Baselines")
        sections.append(markdown_table(["Setting", "Pass Rate", "Passed", "Avg Candidates"], rows))
    if budget:
        rows = []
        for setting, summary in budget["settings"].items():
            rows.append([setting, f"{summary['pass_rate_mean']:.4f}", f"{summary['pass_rate_std']:.4f}", f"{summary['latency_mean']:.2f}"])
        sections.append("## Budget And Cost")
        sections.append(markdown_table(["Setting", "Mean", "Std", "Avg Latency"], rows))
    if selector:
        rows = [[metric, f"{selector[metric]:.4f}"] for metric in ["selector_pass_rate", "always_on_pass_rate", "threshold_like_pass_rate", "oracle_pass_rate"] if metric in selector]
        sections.append("## Action Selector")
        sections.append(markdown_table(["Metric", "Value"], rows))
    if humaneval:
        rows = [[setting, f"{summary['pass_rate']:.4f}", f"{summary['passed']}/{summary['num_episodes']}"] for setting, summary in humaneval["settings"].items()]
        sections.append("## HumanEval+ Full")
        sections.append(markdown_table(["Setting", "Pass Rate", "Passed"], rows))
    write_text(args.out_main, "\n".join(sections) + "\n")

    claim_lines = [
        "# B Claim Matrix",
        "",
        "| Claim | Status | Note |",
        "| --- | --- | --- |",
    ]
    if week1 and "multi_prior_mbrexec" in week1["settings"] and "no_prior_mbrexec" in week1["settings"]:
        multi = week1["settings"]["multi_prior_mbrexec"]["passed"]
        base = week1["settings"]["no_prior_mbrexec"]["passed"]
        status = "supported" if multi - base >= 5 else "qualified"
        claim_lines.append(f"| structure-aware + MBR remains above no-prior + MBR | {status} | diff = {multi - base} solved tasks |")
    if selector:
        if selector.get("selector_pass_rate", 0.0) > selector.get("always_on_pass_rate", 0.0):
            status = "supported"
        elif selector.get("selector_pass_rate", 0.0) == selector.get("always_on_pass_rate", 0.0):
            status = "qualified"
        else:
            status = "unsupported"
        claim_lines.append(f"| action selector improves over always-on | {status} | selector={selector.get('selector_pass_rate', 0.0):.4f}, always-on={selector.get('always_on_pass_rate', 0.0):.4f} |")
    if humaneval and "best_structure" in humaneval["settings"] and "no_prior_mbrexec" in humaneval["settings"]:
        best = humaneval["settings"]["best_structure"]["passed"]
        base = humaneval["settings"]["no_prior_mbrexec"]["passed"]
        if best > base:
            status = "supported"
        elif best == base:
            status = "qualified"
        else:
            status = "unsupported"
        claim_lines.append(f"| external validity on full HumanEval+ | {status} | diff = {best - base} solved tasks |")
    write_text(args.out_claims, "\n".join(claim_lines) + "\n")


if __name__ == "__main__":
    main()
