from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fmt(value: float) -> str:
    return f"{value:.2f}"


def assert_close(label: str, observed: float, expected: float, tolerance: float = 1e-6) -> None:
    if abs(observed - expected) > tolerance:
        raise AssertionError(f"{label}: expected {expected}, observed {observed}")


def assert_equal(label: str, observed: object, expected: object) -> None:
    if observed != expected:
        raise AssertionError(f"{label}: expected {expected!r}, observed {observed!r}")


def pass_map(result_path: str) -> dict[str, bool]:
    payload = load_json(result_path)
    rows: dict[str, bool] = {}
    for row in payload["episodes"]:
        query_id = row["episode"]["query_id"]
        rows[query_id] = bool(row["passed"])
    return rows


def paired_changes(summary: dict[str, Any], setting: str) -> tuple[list[list[int]], tuple[int, int, int], tuple[int, int, int]]:
    no_runs = {row["seed"]: row for row in summary["settings"]["no_prior"]["runs"]}
    setting_runs = {row["seed"]: row for row in summary["settings"][setting]["runs"]}
    per_seed: list[list[int]] = []
    pooled = [0, 0, 0]
    task_delta: dict[str, int] = {}
    for seed in sorted(setting_runs):
        baseline = pass_map(no_runs[seed]["result_path"])
        candidate = pass_map(setting_runs[seed]["result_path"])
        improved = regressed = unchanged = 0
        for query_id in sorted(set(baseline) | set(candidate)):
            delta = int(candidate.get(query_id, False)) - int(baseline.get(query_id, False))
            if delta > 0:
                improved += 1
            elif delta < 0:
                regressed += 1
            else:
                unchanged += 1
            task_delta[query_id] = task_delta.get(query_id, 0) + delta
        per_seed.append([seed, improved, regressed, unchanged, improved - regressed])
        pooled[0] += improved
        pooled[1] += regressed
        pooled[2] += unchanged
    clustered = (
        sum(1 for delta in task_delta.values() if delta > 0),
        sum(1 for delta in task_delta.values() if delta < 0),
        sum(1 for delta in task_delta.values() if delta == 0),
    )
    return per_seed, tuple(pooled), clustered


def setting_block(blocks: list[dict[str, Any]], label_prefix: str, setting: str) -> dict[str, Any]:
    for block in blocks:
        if block["label"].startswith(label_prefix):
            for row in block["settings"]:
                if row["setting"] == setting:
                    return row
    raise KeyError((label_prefix, setting))


def row_for_bin(setting: dict[str, Any], bin_name: str) -> dict[str, Any]:
    for row in setting["rows"]:
        if row["bin"] == bin_name:
            return row
    raise KeyError(bin_name)


def print_section(title: str) -> None:
    print()
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def main() -> None:
    print("SPC-Audit reviewer claim audit")
    print("This script does not trust manuscript prose. It reads packaged JSON result files,")
    print("recomputes the headline quantities, and checks them against the paper claims.")
    print("No LLM calls, no GPU, no network, and no generated-code execution.")

    print_section("1. Main MBPP+224 fair-budget result")
    summary = load_json("results/mbpp224_fair_budget/summary.json")
    for setting, expected_mean, expected_range in [
        ("no_prior", 178.66666666666666, [178, 179]),
        ("single_prior", 181.66666666666666, [181, 183]),
        ("multi_prior", 185.0, [184, 187]),
        ("random_prior", 172.33333333333334, [172, 173]),
        ("corrupted_prior", 173.33333333333334, [172, 175]),
    ]:
        stats = summary["settings"][setting]
        solved = [run["summary"]["passed"] for run in stats["runs"]]
        assert_close(f"{setting} solved_mean", stats["solved_mean"], expected_mean)
        assert_equal(f"{setting} solved_range", stats["solved_range"], expected_range)
        print(f"- {setting:16s}: seeds={solved} mean={fmt(stats['solved_mean'])} range={stats['solved_range']}")
    delta = summary["settings"]["multi_prior"]["solved_mean"] - summary["settings"]["no_prior"]["solved_mean"]
    assert_close("multi_prior minus no_prior", delta, 6.333333333333333)
    print(f"  Interpretation: the supported positive claim is modest and scoped: +{fmt(delta)} solved tasks.")
    print("  Evidence files: results/mbpp224_fair_budget/summary.json and referenced raw result JSONs.")

    print_section("2. Paired directionality")
    per_seed, pooled, clustered = paired_changes(summary, "multi_prior")
    for seed, improved, regressed, unchanged, net in per_seed:
        print(f"- seed {seed}: improved={improved}, regressed={regressed}, unchanged={unchanged}, net={net:+d}")
    assert_equal("pooled improved/regressed/unchanged", pooled, (30, 11, 631))
    assert_equal("task-clustered positive/negative/zero", clustered, (14, 5, 205))
    print(f"- pooled query-seed: improved={pooled[0]}, regressed={pooled[1]}, unchanged={pooled[2]}")
    print(f"- task-clustered: positive={clustered[0]}, negative={clustered[1]}, zero={clustered[2]}")
    print("  Interpretation: positive direction remains after task clustering, but the paper does not claim robustness.")

    print_section("3. Prompt-only structural boundary")
    prompt_summary = load_json("results/prompt_only_structural_mbpp224_fair_budget/summary.json")
    for setting, expected_mean in [
        ("no_prior", 179.33333333333334),
        ("single_prior", 173.66666666666666),
        ("multi_prior", 177.66666666666666),
    ]:
        stats = prompt_summary["settings"][setting]
        solved = [run["summary"]["passed"] for run in stats["runs"]]
        assert_close(f"prompt-only {setting} solved_mean", stats["solved_mean"], expected_mean)
        print(f"- prompt-only {setting:12s}: seeds={solved} mean={fmt(stats['solved_mean'])}")
    print("  Interpretation: full MBPP+224 prompt-only structural retrieval is non-positive.")
    print("  Evidence file: results/prompt_only_structural_mbpp224_fair_budget/summary.json")

    print_section("4. Prior-quality response")
    quality = load_json("paper/tbl_prior_quality_response.json")
    code_multi = setting_block(quality["blocks"], "Code-aware", "multi_prior")
    low = row_for_bin(code_multi, "low")
    medium = row_for_bin(code_multi, "medium")
    high = row_for_bin(code_multi, "high")
    med_high_n = medium["n"] + high["n"]
    med_high_improved = medium["improved"] + high["improved"]
    med_high_regressed = medium["regressed"] + high["regressed"]
    med_high_net = medium["net"] + high["net"]
    med_high_coverage = med_high_n / code_multi["n"]
    assert_equal("code-aware multi low net", low["net"], 2)
    assert_equal("code-aware multi medium/high improved", med_high_improved, 23)
    assert_equal("code-aware multi medium/high regressed", med_high_regressed, 6)
    assert_equal("code-aware multi medium/high net", med_high_net, 17)
    assert_close("code-aware multi medium/high coverage", med_high_coverage, 0.46875)
    print(f"- code-aware multi_prior low bin: coverage={low['coverage']:.3f}, net={low['net']:+d}")
    print(
        "- code-aware multi_prior medium/high bins: "
        f"coverage={med_high_coverage:.3f}, improved={med_high_improved}, "
        f"regressed={med_high_regressed}, net={med_high_net:+d}"
    )

    prompt_multi = setting_block(quality["blocks"], "Prompt-only", "multi_prior")
    prompt_high = row_for_bin(prompt_multi, "high")
    assert_equal("prompt-only high-fidelity N", prompt_high["n"], 6)
    print(f"- prompt-only multi_prior high-fidelity count: {prompt_high['n']} / {prompt_multi['n']}")

    random_prior = setting_block(quality["blocks"], "Code-aware", "random_prior")
    corrupted_prior = setting_block(quality["blocks"], "Code-aware", "corrupted_prior")
    assert_equal("random prior net", random_prior["outcome_counts"]["improved"] - random_prior["outcome_counts"]["regressed"], -19)
    assert_equal(
        "corrupted prior net",
        corrupted_prior["outcome_counts"]["improved"] - corrupted_prior["outcome_counts"]["regressed"],
        -16,
    )
    print("- random_prior outcome net: -19; corrupted_prior outcome net: -16")
    print("  Interpretation: prior presence is not enough; quality coverage and harm rate must be reported.")

    print_section("5. Boundary and non-claims")
    print("- External/backend rows are boundary instantiations, not broad transfer or backend invariance.")
    print("- MBR-exec is same-test diagnostic selection, not deployment-time selection.")
    print("- structure_fidelity is retrospective/reference-code-based, not a deployable quality estimator.")
    print("- Controlled degradation is a secondary noisy diagnostic pilot, not causal proof.")

    print()
    print("[PASS] reviewer claim audit matched the paper's headline numbers and boundaries")


if __name__ == "__main__":
    main()
