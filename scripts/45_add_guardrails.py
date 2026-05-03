from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from guardrails.quick_runtime_check import run_quick_runtime_check
from guardrails.static_checks import infer_required_arity, run_static_checks
from plan_b.io_utils import read_json, write_json
from plan_b.mbpp import load_examples
from rerank.sandbox_runner import run_candidate


def candidate_passes_checks(candidate: dict, entry_point: str, prompt: str, checks: list[str], expected_arity: int | None) -> tuple[bool, dict]:
    diagnostics = {}
    code = candidate.get("code", "")
    static = run_static_checks(code, entry_point=entry_point, prompt=prompt, expected_arity=expected_arity if "arity" in checks else None)
    diagnostics["static"] = static
    keep = True
    if "parse" in checks and not static["parse_ok"]:
        keep = False
    if "function_name" in checks and not static["function_name_ok"]:
        keep = False
    if "arity" in checks and not static["arity_ok"]:
        keep = False
    if "return_type" in checks and not static["return_type_ok"]:
        keep = False
    if keep and "quick_runtime" in checks:
        quick = run_quick_runtime_check(code, entry_point=entry_point, expected_arity=expected_arity, timeout_sec=2)
        diagnostics["quick_runtime"] = quick
        if quick.get("status") not in {"passed", "skipped"} and not quick.get("passed"):
            keep = False
    return keep, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply cheap guardrails to stored Plan B candidates.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--eval-examples", default="data/processed/evalplus/mbppplus_test.jsonl")
    parser.add_argument("--checks", nargs="+", default=["parse", "function_name", "arity", "return_type", "quick_runtime"])
    parser.add_argument("--out", default="results/b_candidates_guarded.json")
    parser.add_argument("--report-out", default="paper/b_week5_guardrail_table.md")
    args = parser.parse_args()

    run = read_json(args.candidates)
    eval_examples = {example.task_id: example for example in load_examples(args.eval_examples)}
    guarded = copy.deepcopy(run)
    passed = 0
    compile_ok = 0
    for row in guarded["episodes"]:
        query_id = row["episode"]["query_id"]
        example = eval_examples[query_id]
        expected_arity = infer_required_arity(example.code)
        filtered = []
        for candidate in row.get("candidates", []):
            keep, diagnostics = candidate_passes_checks(candidate, example.entry_point, example.prompt, args.checks, expected_arity)
            candidate.setdefault("details", {})
            candidate["details"]["guardrails"] = diagnostics
            if keep and candidate.get("passed") is None:
                result = run_candidate(candidate.get("code", ""), example.test, timeout_sec=8)
                candidate["passed"] = bool(result.get("passed"))
                candidate["compile_ok"] = result.get("status") != "failed" or candidate["passed"]
                candidate["exec_status"] = result.get("status")
                candidate["details"]["guardrail_exec"] = result
            if keep:
                filtered.append(candidate)
        row["guarded_candidates"] = filtered
        chosen = next((candidate for candidate in filtered if candidate.get("passed")), filtered[0] if filtered else row["best_candidate"])
        row["guarded_best_candidate"] = chosen
        row["guarded_passed"] = bool(chosen.get("passed"))
        if row["guarded_passed"]:
            passed += 1
        if chosen.get("compile_ok"):
            compile_ok += 1
    guarded["guardrail_pass_rate"] = passed / max(len(guarded["episodes"]), 1)
    guarded["guardrail_compile_ok"] = compile_ok
    write_json(args.out, guarded)

    md = "# Week5 Guardrails\n\n"
    md += "| Metric | Value |\n| --- | ---: |\n"
    md += f"| original_pass_rate | {run['pass_rate']:.4f} |\n"
    md += f"| guardrail_pass_rate | {guarded['guardrail_pass_rate']:.4f} |\n"
    md += f"| guarded_compile_ok | {compile_ok}/{len(guarded['episodes'])} |\n"
    Path(args.report_out).write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
