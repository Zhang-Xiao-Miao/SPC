from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.io_utils import read_json, write_json, write_text


BINS = [
    ("low", 0.0, 0.15),
    ("medium", 0.15, 0.50),
    ("high", 0.50, 1.01),
]

SENSITIVITY_THRESHOLDS = [0.10, 0.15, 0.25, 0.50]


def bin_name(value: float) -> str:
    for name, lower, upper in BINS:
        if lower <= value < upper:
            return name
    return "high" if value >= 0.50 else "low"


def load_episodes(path: Path) -> list[dict]:
    payload = read_json(path)
    return list(payload["episodes"])


def summarize_threshold(records: list[tuple[float, int]], threshold: float) -> dict:
    selected = [(fidelity, delta) for fidelity, delta in records if fidelity >= threshold]
    improved = sum(1 for _, delta in selected if delta > 0)
    regressed = sum(1 for _, delta in selected if delta < 0)
    unchanged = sum(1 for _, delta in selected if delta == 0)
    changed = improved + regressed
    return {
        "threshold": threshold,
        "n": len(selected),
        "coverage": len(selected) / len(records) if records else 0.0,
        "improved": improved,
        "regressed": regressed,
        "unchanged": unchanged,
        "net": improved - regressed,
        "harm_rate": regressed / changed if changed else None,
    }


def summarize_setting(root: Path, prefix: str, setting: str, seeds: list[int]) -> dict:
    bins = {
        name: {
            "n": 0,
            "improved": 0,
            "regressed": 0,
            "unchanged": 0,
            "net": 0,
            "fidelity_sum": 0.0,
        }
        for name, _, _ in BINS
    }
    all_fidelity: list[float] = []
    outcome_fidelity: dict[str, list[float]] = {"improved": [], "regressed": [], "unchanged": []}
    threshold_records: list[tuple[float, int]] = []
    for seed in seeds:
        baseline_path = root / f"{prefix}_no_prior_mbrexec_budget8_seed{seed}.json"
        setting_path = root / f"{prefix}_{setting}_mbrexec_budget8_seed{seed}.json"
        baseline = load_episodes(baseline_path)
        run = load_episodes(setting_path)
        if len(baseline) != len(run):
            raise ValueError(f"Mismatched episode counts for seed {seed}: {baseline_path} vs {setting_path}")
        for base_row, run_row in zip(baseline, run):
            fidelity = float(run_row.get("structure_fidelity", 0.0))
            delta = int(bool(run_row["passed"])) - int(bool(base_row["passed"]))
            threshold_records.append((fidelity, delta))
            target = bins[bin_name(fidelity)]
            target["n"] += 1
            target["fidelity_sum"] += fidelity
            all_fidelity.append(fidelity)
            if delta > 0:
                target["improved"] += 1
                outcome_fidelity["improved"].append(fidelity)
            elif delta < 0:
                target["regressed"] += 1
                outcome_fidelity["regressed"].append(fidelity)
            else:
                target["unchanged"] += 1
                outcome_fidelity["unchanged"].append(fidelity)
            target["net"] += delta
    rows = []
    total_n = sum(row["n"] for row in bins.values())
    for name, _, _ in BINS:
        row = bins[name]
        changed = row["improved"] + row["regressed"]
        rows.append(
            {
                "bin": name,
                "n": row["n"],
                "coverage": row["n"] / total_n if total_n else 0.0,
                "improved": row["improved"],
                "regressed": row["regressed"],
                "unchanged": row["unchanged"],
                "net": row["net"],
                "harm_rate": row["regressed"] / changed if changed else None,
            }
        )
    return {
        "setting": setting,
        "n": total_n,
        "setting_level_mean_fidelity": sum(all_fidelity) / len(all_fidelity) if all_fidelity else 0.0,
        "max_fidelity": max(all_fidelity) if all_fidelity else 0.0,
        "outcome_mean_fidelity": {
            name: (sum(values) / len(values) if values else 0.0)
            for name, values in outcome_fidelity.items()
        },
        "outcome_counts": {name: len(values) for name, values in outcome_fidelity.items()},
        "threshold_sensitivity": [
            summarize_threshold(threshold_records, threshold)
            for threshold in SENSITIVITY_THRESHOLDS
        ],
        "rows": rows,
    }


def format_rate(value: float | None) -> str:
    return "NA" if value is None else f"{value:.3f}"


def make_markdown(payload: dict) -> str:
    lines = [
        "# Retrospective Prior-Quality Response Audit of the Information-Access Boundary",
        "",
        "This table stratifies paired outcomes by the diagnostic `structure_fidelity` field already recorded in the raw run files by `plan_b/pipeline.py`. The audit script reads that stored field; it does not recompute retrieval, rerun generation, tune prompts, tune retrieval, filter episodes, or compute new `structure_fidelity` values for the paper table. The metric compares query reference-code structure with the prior summary through API-call, control-flow, and data-structure overlap. It is a retrospective audit metric, not a deployable prior-construction method.",
        "",
        "Table caption for manuscript use: This table is retrospective and reference-code-based. It is not a deployable prior-quality estimator and is not used to tune retrieval, prompts, generation, or episode selection.",
        "",
        "Bins are fixed in the audit script: `low < 0.15`, `0.15 <= medium < 0.50`, and `high >= 0.50`. These cut points match the earlier project heuristic in `scripts/54_train_usefulness_v2.py` (`fidelity < 0.15` and `fidelity >= 0.5`) and are reported for interpretability, not model selection.",
        "",
        "Reported quantities: `Coverage = N / total_N_for_condition`, `Net Delta = improved - regressed`, and `Harm Rate = regressed / (improved + regressed)`, with `NA` when there are no changed outcomes.",
        "",
    ]
    for block in payload["blocks"]:
        lines.extend(
            [
                f"## {block['label']}",
                "",
                f"- Result root: `{block['root']}`",
                f"- Baseline: `{block['baseline']}`",
                f"- Seeds: `{', '.join(str(seed) for seed in block['seeds'])}`",
                "",
                "| Regime | Setting | Fidelity Bin | N | Coverage | Improved | Regressed | Unchanged | Net Delta | Harm Rate |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for setting in block["settings"]:
            for row in setting["rows"]:
                lines.append(
                    "| {regime} | {setting} | {bin} | {n} | {coverage:.3f} | {improved} | {regressed} | {unchanged} | {net:+d} | {harm_rate} |".format(
                        regime=block["regime"],
                        setting=setting["setting"],
                        bin=row["bin"],
                        n=row["n"],
                        coverage=row["coverage"],
                        improved=row["improved"],
                        regressed=row["regressed"],
                        unchanged=row["unchanged"],
                        net=row["net"],
                        harm_rate=format_rate(row["harm_rate"]),
                    )
                )
        lines.append("")
        lines.extend(
            [
                "Outcome-level fidelity separation, without binning:",
                "",
                "| Setting | Improved N | Improved Fidelity | Regressed N | Regressed Fidelity | Unchanged N | Unchanged Fidelity |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for setting in block["settings"]:
            lines.append(
                "| {setting} | {improved_n} | {improved_mean:.3f} | {regressed_n} | {regressed_mean:.3f} | {unchanged_n} | {unchanged_mean:.3f} |".format(
                    setting=setting["setting"],
                    improved_n=setting["outcome_counts"]["improved"],
                    improved_mean=setting["outcome_mean_fidelity"]["improved"],
                    regressed_n=setting["outcome_counts"]["regressed"],
                    regressed_mean=setting["outcome_mean_fidelity"]["regressed"],
                    unchanged_n=setting["outcome_counts"]["unchanged"],
                    unchanged_mean=setting["outcome_mean_fidelity"]["unchanged"],
                )
            )
        lines.append("")
        lines.extend(
            [
                "Threshold sensitivity for fidelity-qualified subsets:",
                "",
                "| Setting | Fidelity >= Threshold | N | Coverage | Improved | Regressed | Unchanged | Net Delta | Harm Rate |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for setting in block["settings"]:
            for row in setting["threshold_sensitivity"]:
                lines.append(
                    "| {setting} | {threshold:.2f} | {n} | {coverage:.3f} | {improved} | {regressed} | {unchanged} | {net:+d} | {harm_rate} |".format(
                        setting=setting["setting"],
                        threshold=row["threshold"],
                        n=row["n"],
                        coverage=row["coverage"],
                        improved=row["improved"],
                        regressed=row["regressed"],
                        unchanged=row["unchanged"],
                        net=row["net"],
                        harm_rate=format_rate(row["harm_rate"]),
                    )
                )
        lines.append("")
    lines.extend(
        [
            "## Quality-Conditioned Takeaway",
            "",
            "1. Average deltas are insufficient: a prior condition may look weak because it rarely constructs high-fidelity priors.",
            "2. Coverage matters: the full prompt-only rerun has very low high-fidelity coverage.",
            "3. Harm matters: low-quality or misleading priors can increase regressions.",
            "4. The audit is retrospective: `structure_fidelity` uses reference-code structure and is not a deployable estimator.",
            "",
            "## Interpretation",
            "",
            "- In the fixed code-aware `syntax_aware` diagnostic episodes, intended priors show positive net deltas in medium- and high-fidelity bins. This supports a quality-conditioned diagnostic claim rather than a broad structural-prior method claim.",
            "- The unbinned outcome-level fidelity separation provides the same cautionary direction for the main intended prior: in code-aware `multi_prior`, improved outcomes have higher diagnostic fidelity than regressed outcomes (`0.311` vs `0.168`).",
            "- Threshold sensitivity is reported over multiple fixed cutoffs (`0.10`, `0.15`, `0.25`, and `0.50`) to reduce dependence on a single bin boundary. This is still diagnostic stratification, not a threshold-tuned decision rule.",
            "- In the full prompt-only `prompt_structural` rerun, diagnostic-fidelity coverage is much lower and high-fidelity cases are rare. The non-positive prompt-only result is consistent with the boundary claim that this retriever did not construct high-quality priors on full MBPP+224.",
            "- Bad-prior conditions should not be interpreted through fidelity alone: corrupted priors can preserve surface structural overlap while still being misleading. They remain diagnostic stress tests rather than deployable priors.",
            "",
        ]
    )
    return "\n".join(lines)


def make_curve_markdown(payload: dict) -> str:
    lines = [
        "# Prior-Quality Response Curve Source",
        "",
        "This markdown file provides a figure-source table for plotting quality-response curves. The x-axis is the fidelity threshold, and the y-axis can be `Net Delta` or `Harm Rate`.",
        "",
        "Caption for manuscript use: The curve is retrospective and reference-code-based. It is a diagnostic response audit, not a deployable quality estimator.",
        "",
        "| Regime | Setting | Fidelity >= Threshold | Coverage | Net Delta | Harm Rate |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for block in payload["blocks"]:
        for setting in block["settings"]:
            for row in setting["threshold_sensitivity"]:
                lines.append(
                    "| {regime} | {setting} | {threshold:.2f} | {coverage:.3f} | {net:+d} | {harm_rate} |".format(
                        regime=block["regime"],
                        setting=setting["setting"],
                        threshold=row["threshold"],
                        coverage=row["coverage"],
                        net=row["net"],
                        harm_rate=format_rate(row["harm_rate"]),
                    )
                )
    lines.append("")
    return "\n".join(lines)


def build_payload() -> dict:
    blocks = []
    configs = [
        {
            "label": "Code-aware diagnostic `syntax_aware` MBPP+224",
            "regime": "code-aware `syntax_aware`",
            "root": Path("results/mbpp224_fair_budget"),
            "prefix": "mbppplus224_syntax_aware",
            "baseline": "no_prior",
            "settings": ["single_prior", "multi_prior", "random_prior", "corrupted_prior"],
            "seeds": [1, 2, 3],
        },
        {
            "label": "Prompt-only `prompt_structural` MBPP+224",
            "regime": "prompt-only `prompt_structural`",
            "root": Path("results/prompt_only_structural_mbpp224_fair_budget"),
            "prefix": "mbppplus224_prompt_structural",
            "baseline": "no_prior",
            "settings": ["single_prior", "multi_prior"],
            "seeds": [1, 2, 3],
        },
    ]
    for config in configs:
        settings = [
            summarize_setting(config["root"], config["prefix"], setting, config["seeds"])
            for setting in config["settings"]
        ]
        blocks.append(
            {
                "label": config["label"],
                "regime": config["regime"],
                "root": str(config["root"]),
                "baseline": config["baseline"],
                "seeds": config["seeds"],
                "settings": settings,
            }
        )

    return {"bins": BINS, "sensitivity_thresholds": SENSITIVITY_THRESHOLDS, "blocks": blocks}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create prior-quality audit tables from packaged MBPP+224 runs.")
    parser.add_argument("--out-json", default="paper/tbl_prior_quality_audit.json")
    parser.add_argument("--out-md", default="paper/tbl_prior_quality_audit.md")
    parser.add_argument("--out-response-json", default="paper/tbl_prior_quality_response.json")
    parser.add_argument("--out-response-md", default="paper/tbl_prior_quality_response.md")
    parser.add_argument("--out-fig-md", default="paper/fig_prior_quality_response.md")
    args = parser.parse_args()

    payload = build_payload()
    markdown = make_markdown(payload)
    write_json(args.out_json, payload)
    write_text(args.out_md, markdown)
    write_json(args.out_response_json, payload)
    write_text(args.out_response_md, markdown)
    write_text(args.out_fig_md, make_curve_markdown(payload))


if __name__ == "__main__":
    main()
