from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import build_base_config, markdown_table, summarize_run
from plan_b.io_utils import write_json, write_jsonl, write_text
from plan_b.mbpp import load_examples
from plan_b.pipeline import run_pipeline
from plan_b.schema import Episode
from retrieval import syntax_aware


def ensure_humaneval_episodes(train_path: str, eval_path: str, output_path: str, shot: int) -> None:
    target = Path(output_path)
    if target.exists():
        return
    train_examples = load_examples(train_path)
    eval_examples = load_examples(eval_path)
    rows = []
    for query in eval_examples:
        supports = syntax_aware.retrieve(query, train_examples, max(shot, 1))
        rows.append(
            Episode(
                episode_id=f"{query.task_id}_k{shot}_syntax_aware",
                query_id=query.task_id,
                k=shot,
                retrieval_mode="syntax_aware",
                support_ids=[example.task_id for _, example in supports[:shot]],
                query_prompt=query.prompt,
                tests_path="",
                entry_point=query.entry_point,
            ).to_dict()
        )
    write_jsonl(target, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full HumanEval+ Plan B baselines.")
    parser.add_argument("--settings", nargs="+", default=["no_prior_mbrexec", "best_structure"])
    parser.add_argument("--candidate-budget", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", default="results/b_humaneval_full.json")
    parser.add_argument("--paper-out", default="paper/b_week6_external_table.md")
    args = parser.parse_args()

    ensure_humaneval_episodes(
        train_path="data/processed/mbpp/train.jsonl",
        eval_path="data/processed/evalplus/humanevalplus_test.jsonl",
        output_path="data/episodes/humanevalplus_test164_syntax_episodes.jsonl",
        shot=1,
    )

    setting_map = {
        "no_prior_mbrexec": {"prior_mode": "none", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 0},
        "best_structure": {"prior_mode": "multi_candidate", "gate_mode": "none", "rerank_mode": "mbr_exec", "num_prior_candidates": 2},
    }
    payload = {"settings": {}}
    rows = []
    for setting in args.settings:
        config = build_base_config("humanevalplus164", "syntax_aware", args.candidate_budget, seed=args.seed)
        config.update(setting_map[setting])
        result_path = f"results/humanevalplus164_syntax_{setting}_budget{args.candidate_budget}_seed{args.seed}.json"
        config["result_path"] = result_path
        result = run_pipeline(config)
        write_json(result_path, result)
        summary = summarize_run(result)
        summary["result_path"] = result_path
        payload["settings"][setting] = summary
        rows.append([setting, f"{summary['pass_rate']:.4f}", f"{summary['passed']}/{summary['num_episodes']}", f"{summary['avg_latency_sec']:.2f}"])
    write_json(args.out, payload)
    md = "# Week6 HumanEval+ Full\n\n"
    md += markdown_table(["Setting", "Pass Rate", "Passed", "Avg Latency"], rows)
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
