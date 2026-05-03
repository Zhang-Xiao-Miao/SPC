from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import BASE_GENERATION_CONFIG, markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text


SETTING_MAP = {
    "no_prior": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "intended_multi": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
    "drop_api_tags": {
        "prior_mode": "multi_candidate",
        "prior_degradation": "drop_api_tags",
        "gate_mode": "none",
        "rerank_mode": "mbr_exec",
        "num_prior_candidates": 2,
    },
    "drop_control_flow_tags": {
        "prior_mode": "multi_candidate",
        "prior_degradation": "drop_control_flow_tags",
        "gate_mode": "none",
        "rerank_mode": "mbr_exec",
        "num_prior_candidates": 2,
    },
    "drop_data_structure_tags": {
        "prior_mode": "multi_candidate",
        "prior_degradation": "drop_data_structure_tags",
        "gate_mode": "none",
        "rerank_mode": "mbr_exec",
        "num_prior_candidates": 2,
    },
    "replace_25": {
        "prior_mode": "multi_candidate",
        "prior_degradation": "replace_25",
        "gate_mode": "none",
        "rerank_mode": "mbr_exec",
        "num_prior_candidates": 2,
    },
    "replace_50": {
        "prior_mode": "multi_candidate",
        "prior_degradation": "replace_50",
        "gate_mode": "none",
        "rerank_mode": "mbr_exec",
        "num_prior_candidates": 2,
    },
    "replace_75": {
        "prior_mode": "multi_candidate",
        "prior_degradation": "replace_75",
        "gate_mode": "none",
        "rerank_mode": "mbr_exec",
        "num_prior_candidates": 2,
    },
    "random_prior": {"prior_mode": "random", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "corrupted_prior": {"prior_mode": "corrupted", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
}


def result_path(args: argparse.Namespace, setting: str) -> Path:
    root = Path("results/degradation_sweep")
    root.mkdir(parents=True, exist_ok=True)
    return root / (
        f"{args.result_prefix}_syntax_aware_{setting}_mbrexec_budget{args.candidate_budget}_"
        f"seed{args.seed}_n{args.max_episodes}.json"
    )


def paired_counts(baseline: dict, run: dict) -> dict:
    improved = regressed = unchanged = 0
    for base_row, run_row in zip(baseline["episodes"], run["episodes"]):
        delta = int(bool(run_row["passed"])) - int(bool(base_row["passed"]))
        if delta > 0:
            improved += 1
        elif delta < 0:
            regressed += 1
        else:
            unchanged += 1
    return {
        "improved": improved,
        "regressed": regressed,
        "unchanged": unchanged,
        "net": improved - regressed,
        "harm_rate": regressed / (improved + regressed) if improved + regressed else None,
    }


def diagnostic_rates(payload: dict) -> dict:
    episodes = payload["episodes"]
    candidates = [candidate for row in episodes for candidate in row.get("candidates", [])]
    selected = [row.get("best_candidate", {}) for row in episodes]
    compile_fail = sum(1 for candidate in candidates if not bool(candidate.get("compile_ok")))
    selected_timeout = sum(1 for candidate in selected if candidate.get("exec_status") == "timeout")
    selected_fail = sum(1 for candidate in selected if not bool(candidate.get("passed")))
    fidelity_values = [float(row.get("structure_fidelity", 0.0)) for row in episodes]
    return {
        "all_candidate_compile_fail_rate": compile_fail / len(candidates) if candidates else 0.0,
        "selected_timeout_rate": selected_timeout / len(selected) if selected else 0.0,
        "selected_fail_rate": selected_fail / len(selected) if selected else 0.0,
        "mean_structure_fidelity": sum(fidelity_values) / len(fidelity_values) if fidelity_values else 0.0,
        "high_fidelity_coverage": sum(1 for value in fidelity_values if value >= 0.50) / len(fidelity_values) if fidelity_values else 0.0,
    }


def fmt_rate(value: float | None) -> str:
    return "NA" if value is None else f"{value:.3f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a controlled prior-quality degradation sweep.")
    parser.add_argument("--settings", default=",".join(SETTING_MAP))
    parser.add_argument("--candidate-budget", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--max-episodes", type=int, default=50)
    parser.add_argument("--generator-backend", default=None)
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--cached-only",
        action="store_true",
        help="Regenerate the summary/table only from existing raw result files; fail instead of running live inference.",
    )
    parser.add_argument("--result-prefix", default="mbppplus50_deepseek_degradation")
    parser.add_argument("--out", default="results/degradation_sweep/summary_seed1_n50.json")
    parser.add_argument("--paper-out", default="paper/tbl_controlled_degradation_sweep.md")
    args = parser.parse_args()

    settings = [item.strip() for item in args.settings.split(",") if item.strip()]
    payload = {
        "dataset": "MBPP+100 first slice",
        "max_episodes": args.max_episodes,
        "candidate_budget": args.candidate_budget,
        "seed": args.seed,
        "generator_backend": args.generator_backend,
        "model_name": args.model_name,
        "settings": {},
        "boundary": "Controlled degradation sweep over a fixed MBPP+ slice; diagnostic evidence, not causal proof.",
    }
    raw_results: dict[str, dict] = {}
    for setting in settings:
        if setting not in SETTING_MAP:
            raise ValueError(f"Unknown setting: {setting}")
        path = result_path(args, setting)
        if path.exists():
            result = read_json(path)
        elif args.cached_only:
            raise FileNotFoundError(
                f"Missing cached degradation result for {setting}: {path}. "
                "Remove --cached-only only when intentionally running live inference."
            )
        else:
            from plan_b.pipeline import run_pipeline

            config = dict(BASE_GENERATION_CONFIG)
            config.update(
                {
                    "dataset": "mbppplus",
                    "train_examples": "data/processed/mbpp/train.jsonl",
                    "eval_examples": "data/processed/evalplus/mbppplus_test.jsonl",
                    "episodes_path": "data/episodes/mbppplus_test100_episodes.jsonl",
                    "k_support": 1,
                    "retrieval_mode": "syntax_aware",
                    "max_episodes": args.max_episodes,
                    "candidate_budget": args.candidate_budget,
                    "seed": args.seed,
                    "device": args.device,
                }
            )
            if args.generator_backend:
                config["generator_backend"] = args.generator_backend
            if args.model_name:
                config["model_name"] = args.model_name
            if args.api_base:
                config["api_base"] = args.api_base
            config.update(SETTING_MAP[setting])
            config["result_path"] = str(path)
            result = run_pipeline(config)
            write_json(path, result)
        raw_results[setting] = result

    baseline = raw_results["no_prior"]
    rows = []
    for setting in settings:
        result = raw_results[setting]
        summary = summarize_run(result)
        paired = paired_counts(baseline, result) if setting != "no_prior" else {"improved": 0, "regressed": 0, "unchanged": summary["num_episodes"], "net": 0, "harm_rate": None}
        diagnostics = diagnostic_rates(result)
        payload["settings"][setting] = {
            "summary": summary,
            "paired_vs_no_prior": paired,
            "diagnostics": diagnostics,
            "result_path": str(result_path(args, setting)),
        }
        rows.append(
            [
                setting,
                f"{summary['passed']}/{summary['num_episodes']}",
                f"{paired['net']:+d}",
                paired["improved"],
                paired["regressed"],
                fmt_rate(paired["harm_rate"]),
                f"{diagnostics['mean_structure_fidelity']:.3f}",
                f"{diagnostics['high_fidelity_coverage']:.3f}",
                f"{diagnostics['all_candidate_compile_fail_rate']:.3f}",
            ]
        )

    write_json(args.out, payload)
    md = "# Controlled Prior-Quality Degradation Sweep\n\n"
    md += "This is a diagnostic sweep over a fixed MBPP+ slice. It treats degraded structural priors as boundary evidence, not as causal proof or a deployable prior-quality estimator.\n\n"
    md += f"- Slice size: `{args.max_episodes}` from `MBPP+100`\n"
    md += f"- Candidate budget: `{args.candidate_budget}`\n"
    md += f"- Seed: `{args.seed}`\n"
    md += f"- Backend: `{args.model_name}` via `{args.generator_backend}`\n\n"
    md += markdown_table(
        [
            "Setting",
            "Solved",
            "Net",
            "Improved",
            "Regressed",
            "Harm",
            "Mean Diagnostic Fidelity",
            "High Coverage",
            "Compile-Fail",
        ],
        rows,
    )
    md += "\n\nBoundary: include positive, negative, and noisy rows. Do not present this sweep as a causal proof or as a replacement for the main prior-quality response audit.\n"
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
