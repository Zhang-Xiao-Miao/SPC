from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import BASE_GENERATION_CONFIG, markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text
from plan_b.pipeline import run_pipeline


SETTING_MAP = {
    "no_prior": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
    "single_prior": {"prior_mode": "single", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 1},
    "multi_prior": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
}


def result_path(prefix: str, dataset: str, setting: str, seed: int) -> str:
    return f"results/{prefix}_{dataset}_syntax_aware_{setting}_mbrexec_budget8_seed{seed}.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a safe cross-model MBPP+100 check without overwriting main vLLM artifacts.")
    parser.add_argument("--prefix", default="hf_safe")
    parser.add_argument("--dataset", default="mbppplus100")
    parser.add_argument("--settings", default="no_prior,multi_prior")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--generator-backend", default="vllm_openai")
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--api-base")
    parser.add_argument("--out", default="results/cross_model_safe_summary.json")
    parser.add_argument("--paper-out", default="paper/tbl_cross_model_safe.md")
    args = parser.parse_args()

    rows = []
    payload = {
        "dataset": args.dataset,
        "seed": args.seed,
        "generator_backend": args.generator_backend,
        "model_name": args.model_name,
        "device": args.device,
        "settings": {},
    }
    settings = [item.strip() for item in args.settings.split(",") if item.strip()]
    for setting in settings:
        config = dict(BASE_GENERATION_CONFIG)
        config.update(
            {
                "dataset": "mbppplus",
                "train_examples": "data/processed/mbpp/train.jsonl",
                "eval_examples": "data/processed/evalplus/mbppplus_test.jsonl",
                "episodes_path": "data/episodes/mbppplus_test100_episodes.jsonl",
                "k_support": 1,
                "retrieval_mode": "syntax_aware",
                "max_episodes": 100,
                "candidate_budget": 8,
                "seed": args.seed,
                "generator_backend": args.generator_backend,
                "model_name": args.model_name,
                "device": args.device,
            }
        )
        if args.api_base:
            config["api_base"] = args.api_base
        config.update(SETTING_MAP[setting])
        config["result_path"] = result_path(args.prefix, args.dataset, setting, args.seed)
        result = run_pipeline(config)
        write_json(config["result_path"], result)
        summary = summarize_run(result)
        payload["settings"][setting] = {"summary": summary, "result_path": config["result_path"]}
        rows.append(
            [setting, f"{summary['pass_rate']:.4f}", f"{summary['passed']}/{summary['num_episodes']}", f"{summary['avg_latency_sec']:.2f}"]
        )

    write_json(args.out, payload)
    md = "# Safe Cross-Model Check\n\n"
    md += markdown_table(["Setting", "Pass Rate", "Passed", "Avg Latency"], rows)
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
