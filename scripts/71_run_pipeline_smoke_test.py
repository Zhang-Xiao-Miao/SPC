from __future__ import annotations

import argparse
import importlib
import tempfile
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.io_utils import write_json, write_jsonl
from plan_b.pipeline import run_pipeline
from plan_b.schema import Episode, Example


CORE_MODULES = [
    "generation.modeling",
    "retrieval.prompt_structural",
    "rerank.mbr_exec",
    "eval.eval_passk",
]


def check_core_imports() -> None:
    for module in CORE_MODULES:
        importlib.import_module(module)


def make_example(task_id: str, prompt: str, code: str, test: str, entry_point: str, split: str) -> dict:
    return Example(
        task_id=task_id,
        prompt=prompt,
        code=code,
        test=test,
        entry_point=entry_point,
        split=split,
        metadata={"source": "artifact_smoke_test"},
    ).to_dict()


def write_fixture(root: Path) -> dict[str, Path]:
    data_dir = root / "data"
    results_dir = root / "results"
    data_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    train_path = data_dir / "train.jsonl"
    eval_path = data_dir / "eval.jsonl"
    episodes_path = data_dir / "episodes.jsonl"

    train_rows = [
        make_example(
            "toy_support_increment",
            "Write a function increment(x) that returns x plus one.",
            "def increment(x):\n    return x + 1\n",
            "assert increment(1) == 2\nassert increment(-1) == 0\n",
            "increment",
            "train",
        ),
        make_example(
            "toy_support_square",
            "Write a function square(x) that returns x squared.",
            "def square(x):\n    return x * x\n",
            "assert square(3) == 9\nassert square(-4) == 16\n",
            "square",
            "train",
        ),
    ]
    eval_rows = [
        make_example(
            "toy_eval_increment",
            "Write a function increment(x) that returns x plus one.",
            "def increment(x):\n    return x + 1\n",
            "assert increment(3) == 4\nassert increment(0) == 1\n",
            "increment",
            "eval",
        )
    ]
    episode_rows = [
        Episode(
            episode_id="toy_eval_increment_k1_syntax_aware",
            query_id="toy_eval_increment",
            k=1,
            retrieval_mode="syntax_aware",
            support_ids=["toy_support_increment"],
            query_prompt="Write a function increment(x) that returns x plus one.",
            tests_path="",
            entry_point="increment",
        ).to_dict()
    ]

    write_jsonl(train_path, train_rows)
    write_jsonl(eval_path, eval_rows)
    write_jsonl(episodes_path, episode_rows)
    return {
        "train": train_path,
        "eval": eval_path,
        "episodes": episodes_path,
        "results": results_dir,
    }


def run_condition(paths: dict[str, Path], setting: str, result_path: Path) -> dict:
    config = {
        "dataset": "toy",
        "train_examples": str(paths["train"]),
        "eval_examples": str(paths["eval"]),
        "episodes_path": str(paths["episodes"]),
        "retrieval_mode": "syntax_aware",
        "k_support": 1,
        "generator_backend": "retrieval_edit",
        "model_name": None,
        "api_base": None,
        "device": "cpu",
        "candidate_budget": 2,
        "temperature": 0.0,
        "timeout_sec": 3,
        "max_new_tokens": 64,
        "seed": 1,
        "gate_mode": "none",
        "rerank_mode": "mbr_exec",
        "result_path": str(result_path),
    }
    if setting == "no_prior":
        config.update({"prior_mode": "none", "num_prior_candidates": 0})
    elif setting == "multi_prior":
        config.update({"prior_mode": "multi_candidate", "num_prior_candidates": 2})
    else:
        raise ValueError(setting)
    result = run_pipeline(config)
    write_json(result_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny local smoke test through the real SPC-Audit pipeline code.")
    parser.add_argument("--work-dir", default="", help="Optional output directory. Defaults to a temporary directory.")
    parser.add_argument("--keep", action="store_true", help="Keep temporary files and print their location.")
    args = parser.parse_args()

    check_core_imports()

    if args.work_dir:
        root = Path(args.work_dir)
        root.mkdir(parents=True, exist_ok=True)
        cleanup = None
    else:
        cleanup = tempfile.TemporaryDirectory(prefix="spc_audit_smoke_")
        root = Path(cleanup.name)

    paths = write_fixture(root)
    no_prior = run_condition(paths, "no_prior", paths["results"] / "toy_no_prior.json")
    multi_prior = run_condition(paths, "multi_prior", paths["results"] / "toy_multi_prior.json")

    no_passed = sum(1 for row in no_prior["episodes"] if row["passed"])
    multi_passed = sum(1 for row in multi_prior["episodes"] if row["passed"])
    if no_passed != 1 or multi_passed != 1:
        raise AssertionError(f"Smoke test expected both conditions to pass one toy task, got {no_passed}, {multi_passed}")

    print("SPC-Audit pipeline smoke test")
    print("[PASS] project modules import")
    print("- Built a one-task toy dataset under:", root)
    print("- Ran real plan_b.pipeline.run_pipeline twice: no_prior and multi_prior")
    print("- Generator backend: retrieval_edit (no LLM, no GPU, no network)")
    print("- Selector: mbr_exec on toy tests, so this does execute generated Python in the sandbox runner")
    print(f"- no_prior solved: {no_passed}/1")
    print(f"- multi_prior solved: {multi_passed}/1")
    print("[PASS] real pipeline code path is executable on a local toy fixture")
    print("[PASS] no LLM, GPU, network, or external benchmark assets required")
    print("Boundary: this is a code-path smoke test, not paper evidence.")

    if args.keep or args.work_dir:
        print("Smoke-test files kept at:", root)
    elif cleanup is not None:
        cleanup.cleanup()


if __name__ == "__main__":
    main()
