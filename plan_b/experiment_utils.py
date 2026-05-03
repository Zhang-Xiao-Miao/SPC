from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Dict, Iterable, List

from plan_b.io_utils import read_json, write_json, write_text


DATASET_PRESETS: Dict[str, Dict[str, object]] = {
    "mbppplus100": {
        "dataset": "mbppplus",
        "train_examples": "data/processed/mbpp/train.jsonl",
        "eval_examples": "data/processed/evalplus/mbppplus_test.jsonl",
        "episodes_path": "data/episodes/mbppplus_test100_episodes.jsonl",
        "k_support": 1,
        "retrieval_mode": "syntax_aware",
        "max_episodes": 100,
    },
    "mbppplus224": {
        "dataset": "mbppplus",
        "train_examples": "data/processed/mbpp/train.jsonl",
        "eval_examples": "data/processed/evalplus/mbppplus_test.jsonl",
        "episodes_path": "data/episodes/mbppplus_test224_episodes.jsonl",
        "k_support": 1,
        "retrieval_mode": "syntax_aware",
        "max_episodes": 224,
    },
    "humanevalplus164": {
        "dataset": "humanevalplus",
        "train_examples": "data/processed/mbpp/train.jsonl",
        "eval_examples": "data/processed/evalplus/humanevalplus_test.jsonl",
        "episodes_path": "data/episodes/humanevalplus_test164_syntax_episodes.jsonl",
        "k_support": 1,
        "retrieval_mode": "syntax_aware",
        "max_episodes": 164,
    },
    "humanevalplus50": {
        "dataset": "humanevalplus",
        "train_examples": "data/processed/mbpp/train.jsonl",
        "eval_examples": "data/processed/evalplus/humanevalplus_test.jsonl",
        "episodes_path": "data/episodes/humanevalplus_test50_syntax_episodes.jsonl",
        "k_support": 1,
        "retrieval_mode": "syntax_aware",
        "max_episodes": 50,
    },
    "humanevalplus20": {
        "dataset": "humanevalplus",
        "train_examples": "data/processed/mbpp/train.jsonl",
        "eval_examples": "data/processed/evalplus/humanevalplus_test.jsonl",
        "episodes_path": "data/episodes/humanevalplus_test20_episodes.jsonl",
        "k_support": 1,
        "retrieval_mode": "syntax_aware",
        "max_episodes": 20,
    },
}


BASE_GENERATION_CONFIG: Dict[str, object] = {
    "generator_backend": "vllm_openai",
    "model_name": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "api_base": "http://127.0.0.1:8000/v1",
    "device": "cpu",
    "temperature": 0.4,
    "timeout_sec": 8,
    "max_new_tokens": 200,
    "entropy_threshold": 1.2,
    "seed": 1,
}


def build_base_config(dataset_key: str, retrieval_mode: str, candidate_budget: int, seed: int = 1) -> Dict[str, object]:
    config = deepcopy(BASE_GENERATION_CONFIG)
    config.update(deepcopy(DATASET_PRESETS[dataset_key]))
    config["retrieval_mode"] = retrieval_mode
    config["candidate_budget"] = candidate_budget
    config["seed"] = seed
    return config


def summarize_run(result: Dict[str, object]) -> Dict[str, object]:
    episodes = result.get("episodes", [])
    passed = sum(1 for row in episodes if row.get("passed"))
    compile_ok = sum(1 for row in episodes if row.get("best_candidate", {}).get("compile_ok"))
    timeout = sum(1 for row in episodes if row.get("best_candidate", {}).get("exec_status") == "timeout")
    failed = len(episodes) - passed
    total_candidates = sum(int(row.get("num_candidates", 0)) for row in episodes)
    prompt_tokens = 0
    completion_tokens = 0
    latency_sec = 0.0
    for row in episodes:
        best = row.get("best_candidate", {})
        details = best.get("details", {})
        prompt_tokens += int(details.get("prompt_tokens", 0))
        completion_tokens += int(details.get("completion_tokens", 0))
        latency_sec += float(details.get("latency_sec", 0.0))
    count = max(len(episodes), 1)
    return {
        "pass_rate": passed / count,
        "passed": passed,
        "num_episodes": len(episodes),
        "compile_ok": compile_ok,
        "failed": failed,
        "timeout": timeout,
        "candidate_budget_total": total_candidates,
        "avg_candidates_per_episode": total_candidates / count,
        "prompt_tokens_total": prompt_tokens,
        "completion_tokens_total": completion_tokens,
        "avg_latency_sec": latency_sec / count,
    }


def markdown_table(headers: List[str], rows: Iterable[Iterable[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---:" if i else "---" for i, _ in enumerate(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines) + "\n"


def write_json_and_md(json_path: str | Path, payload: object, md_path: str | Path, content: str) -> None:
    write_json(json_path, payload)
    write_text(md_path, content)


def load_run(path: str | Path) -> Dict[str, object]:
    return read_json(path)
