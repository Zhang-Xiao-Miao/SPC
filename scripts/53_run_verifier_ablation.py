from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.io_utils import read_json, write_json, write_text
from plan_b.mbpp import load_examples
from verifier.learned_verifier import CandidateFeatureRow, LearnedVerifierModel, candidate_feature_map
from verifier.smoke_exec import run_quick_runtime_check
from verifier.static_guardrails import infer_required_arity, run_static_checks


def parse_run_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def passes_static(candidate: dict, example: object) -> tuple[bool, dict]:
    expected_arity = infer_required_arity(example.code)
    static = run_static_checks(candidate.get("code", ""), example.entry_point, example.prompt, expected_arity=expected_arity)
    keep = bool(static.get("parse_ok")) and bool(static.get("function_name_ok")) and bool(static.get("arity_ok")) and bool(static.get("return_type_ok"))
    return keep, static


def passes_smoke(candidate: dict, example: object, timeout_sec: int) -> tuple[bool, dict]:
    expected_arity = infer_required_arity(example.code)
    smoke = run_quick_runtime_check(
        candidate.get("code", ""),
        example.entry_point,
        expected_arity=expected_arity,
        timeout_sec=timeout_sec,
    )
    keep = bool(smoke.get("passed")) or smoke.get("status") == "skipped"
    return keep, smoke


def choose_first(candidates: list[dict], fallback: dict) -> dict:
    return candidates[0] if candidates else fallback


def choose_with_verifier(candidates: list[dict], episode_row: dict, example: object, model: LearnedVerifierModel) -> dict:
    if not candidates:
        return episode_row["best_candidate"]
    rows = []
    for index, candidate in enumerate(candidates):
        fmap = candidate_feature_map(candidate, episode_row, example, index, include_smoke=False)
        rows.append(
            CandidateFeatureRow(
                query_id=episode_row["episode"]["query_id"],
                entry_point=example.entry_point,
                candidate_index=index,
                label=1 if candidate.get("passed") else 0,
                features=list(fmap.values()),
                feature_map=fmap,
                metadata={},
            )
        )
    scores = model.predict_scores(rows)
    best_index = max(range(len(candidates)), key=lambda idx: scores[idx])
    chosen = copy.deepcopy(candidates[best_index])
    chosen.setdefault("details", {})
    chosen["details"]["verifier_score"] = scores[best_index]
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description="Run verifier stack ablation on stored Plan B candidates.")
    parser.add_argument("--runs", required=True, help="Comma-separated run JSON files.")
    parser.add_argument("--eval-examples", default="data/processed/evalplus/mbppplus_test.jsonl")
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-episodes", type=int, default=None)
    parser.add_argument("--smoke-timeout-sec", type=int, default=2)
    parser.add_argument("--out", default="results/verifier_ablation.json")
    parser.add_argument("--paper-out", default="paper/b_verifier_ablation.md")
    args = parser.parse_args()

    eval_index = {example.task_id: example for example in load_examples(args.eval_examples)}
    model = LearnedVerifierModel.load(args.model)

    summary_rows = []
    payload = {"runs": []}
    for run_path in parse_run_list(args.runs):
        run = read_json(run_path)
        episodes = run.get("episodes", [])
        if args.max_episodes is not None:
            episodes = episodes[: args.max_episodes]
        counts = {
            "original_mbr": 0,
            "guardrails_only": 0,
            "guardrails_smoke_mbr": 0,
            "guardrails_smoke_mbr_verifier": 0,
        }
        detailed_rows = []
        for episode_row in episodes:
            query_id = episode_row["episode"]["query_id"]
            example = eval_index[query_id]
            original = episode_row["best_candidate"]
            static_kept = []
            smoke_kept = []
            for candidate in episode_row.get("candidates", []):
                keep_static, static = passes_static(candidate, example)
                candidate.setdefault("details", {})
                candidate["details"]["static_guardrails"] = static
                if keep_static:
                    static_kept.append(candidate)
                    keep_smoke, smoke = passes_smoke(candidate, example, timeout_sec=args.smoke_timeout_sec)
                    candidate["details"]["smoke_exec"] = smoke
                    if keep_smoke:
                        smoke_kept.append(candidate)
            guardrails_only = choose_first(static_kept, original)
            smoke_then_mbr = choose_first(smoke_kept, guardrails_only)
            smoke_then_verifier = choose_with_verifier(smoke_kept, episode_row, example, model)
            stage_choices = {
                "original_mbr": original,
                "guardrails_only": guardrails_only,
                "guardrails_smoke_mbr": smoke_then_mbr,
                "guardrails_smoke_mbr_verifier": smoke_then_verifier,
            }
            for stage, chosen in stage_choices.items():
                if chosen.get("passed"):
                    counts[stage] += 1
            detailed_rows.append(
                {
                    "query_id": query_id,
                    "original_passed": bool(original.get("passed")),
                    "guardrails_only_passed": bool(guardrails_only.get("passed")),
                    "guardrails_smoke_mbr_passed": bool(smoke_then_mbr.get("passed")),
                    "guardrails_smoke_mbr_verifier_passed": bool(smoke_then_verifier.get("passed")),
                }
            )
        num_episodes = max(len(episodes), 1)
        metrics = {stage: value / num_episodes for stage, value in counts.items()}
        payload["runs"].append(
            {
                "run_path": run_path,
                "num_episodes_evaluated": num_episodes,
                "counts": counts,
                "metrics": metrics,
                "details": detailed_rows,
            }
        )
        summary_rows.append(
            [
                Path(run_path).name,
                f"{metrics['original_mbr']:.4f}",
                f"{metrics['guardrails_only']:.4f}",
                f"{metrics['guardrails_smoke_mbr']:.4f}",
                f"{metrics['guardrails_smoke_mbr_verifier']:.4f}",
            ]
        )

    write_json(args.out, payload)
    md = "# Verifier Stack Ablation\n\n"
    md += "| Run | Original MBR | Guardrails Only | Guardrails+Smoke+MBR | Guardrails+Smoke+MBR+Verifier |\n"
    md += "| --- | ---: | ---: | ---: | ---: |\n"
    for row in summary_rows:
        md += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |\n"
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
