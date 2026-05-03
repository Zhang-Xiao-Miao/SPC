from __future__ import annotations

from pathlib import Path
import ast
import copy
import random
import warnings
from typing import Dict, List

from generation.modeling import LocalGenerator
from gating.threshold_gate import gate as threshold_gate
from gating.threshold_gate import entropy as counter_entropy
from plan_b.io_utils import read_jsonl
from plan_b.mbpp import load_examples
from plan_b.schema import Episode, Example, PriorCandidate
from rerank.sandbox_runner import run_candidate
from rerank.mbr_exec import rerank_candidates
from retrieval import dense as dense_retrieval
from retrieval import lexical as lexical_retrieval
from retrieval import prompt_structural as prompt_structural_retrieval
from retrieval import syntax_aware as syntax_retrieval
from structure.extract_ast import extract_structure, summarize_support_structures
from structure.induce_union import induce_union
from structure.induce_vote import induce_vote


RETRIEVERS = {
    "lexical": lexical_retrieval.retrieve,
    "dense": dense_retrieval.retrieve,
    "prompt_structural": prompt_structural_retrieval.retrieve,
    "syntax_aware": syntax_retrieval.retrieve,
    "usefulness_rerank": syntax_retrieval.retrieve,
    "usefulness_v2": syntax_retrieval.retrieve,
}


def _load_episode_index(path: str | Path) -> List[Episode]:
    rows = read_jsonl(path)
    return [Episode(**row) for row in rows]


def _example_by_id(examples: List[Example]) -> Dict[str, Example]:
    return {example.task_id: example for example in examples}


def run_pipeline(config: Dict[str, object]) -> Dict[str, object]:
    rng = random.Random(int(config.get("seed", 1)))
    train_examples = load_examples(config["train_examples"])
    eval_examples = load_examples(config["eval_examples"])
    eval_index = _example_by_id(eval_examples)
    train_index = _example_by_id(train_examples)
    episodes = _load_episode_index(config["episodes_path"])
    retriever = RETRIEVERS[config["retrieval_mode"]]
    generator = LocalGenerator(
        generator_name=config.get("generator_backend", "retrieval_edit"),
        model_name=config.get("model_name"),
        device=config.get("device", "cpu"),
        max_new_tokens=int(config.get("max_new_tokens", 192)),
        api_base=config.get("api_base"),
    )
    gate_mode = config.get("gate_mode", "threshold")
    rerank_mode = config.get("rerank_mode", "mbr_exec")
    candidate_budget = int(config.get("candidate_budget", 0))

    target_retrieval = config.get("retrieval_mode")
    target_k = config.get("k_support")
    max_episodes = int(config.get("max_episodes", 0))

    selected = []
    for episode in episodes:
        if target_retrieval is not None and episode.retrieval_mode != target_retrieval:
            continue
        if target_k is not None and int(episode.k) != int(target_k):
            continue
        selected.append(episode)
        if max_episodes and len(selected) >= max_episodes:
            break

    episode_results = []
    for episode in selected:
        query = eval_index[episode.query_id]
        supports = [train_index[support_id] for support_id in episode.support_ids]
        retrieval_scores = [score for score, _ in retriever(query, train_examples, max(episode.k, 1))]
        counts = summarize_support_structures([support.code for support in supports])
        entropy_values = [counter_entropy(counter) for counter in counts.values() if counter]
        mean_entropy = sum(entropy_values) / len(entropy_values) if entropy_values else 0.0
        mean_retrieval = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
        prior_mode = config.get("prior_mode", "none")
        if prior_mode == "single":
            priors = induce_union(counts, top_m=int(config.get("num_prior_candidates", 1)))
        elif prior_mode == "multi_candidate":
            priors = induce_vote(counts, top_m=int(config.get("num_prior_candidates", 3)))
        elif prior_mode == "oracle":
            priors = [build_oracle_prior(query)]
        elif prior_mode == "random":
            priors = build_random_priors(train_examples, rng, int(config.get("num_prior_candidates", 1)))
        elif prior_mode == "corrupted":
            priors = [corrupt_prior(build_oracle_prior(query), train_examples, rng)]
        elif prior_mode == "weak":
            priors = [build_weak_prior(counts)]
        else:
            priors = []
        degradation_mode = config.get("prior_degradation")
        if degradation_mode and priors:
            priors = degrade_priors(priors, train_examples, rng, str(degradation_mode))
        all_candidates = []
        gate_records = []
        if not priors:
            priors = [None]
        sample_counts = allocate_candidate_budget(
            num_variants=len(priors),
            candidate_budget=candidate_budget,
            default_per_variant=int(config.get("num_samples_per_prior", 2)),
        )
        for prior, num_samples in zip(priors, sample_counts):
            if num_samples <= 0:
                continue
            gate_state = {"use_prior": False}
            if prior is not None and gate_mode == "threshold":
                gate_state = threshold_gate(
                    prior,
                    counts,
                    retrieval_scores,
                    entropy_threshold=float(config.get("entropy_threshold", 1.2)),
                )
            elif prior is not None and gate_mode == "none":
                gate_state = {
                    "use_prior": True,
                    "mean_entropy": None,
                    "mean_retrieval": sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0,
                    "prior_score": prior.score,
                }
            gate_records.append({"prior": prior.to_dict() if prior is not None else None, **gate_state})
            active_prior = prior if gate_state.get("use_prior") else None
            all_candidates.extend(
                generator.generate(
                    query,
                    supports,
                    active_prior,
                    num_samples=num_samples,
                    temperature=float(config.get("temperature", 0.2)),
                )
            )
        if rerank_mode == "mbr_exec":
            best, reranked = rerank_candidates(
                all_candidates,
                query.test,
                timeout_sec=int(config.get("timeout_sec", 5)),
            )
        else:
            best = all_candidates[0]
            result = run_candidate(best.code, query.test, timeout_sec=int(config.get("timeout_sec", 5)))
            best.exec_status = str(result["status"])
            best.passed = bool(result["passed"])
            best.details.update(result)
            best.compile_ok = result["status"] != "failed" or best.passed
            reranked = all_candidates
        query_structure = extract_structure(query.code)
        fidelity = structure_fidelity(query_structure.to_dict(), priors)
        episode_results.append(
            {
                "episode": episode.to_dict(),
                "best_candidate": best.to_dict(),
                "candidates": [candidate.to_dict() for candidate in reranked],
                "num_candidates": len(all_candidates),
                "passed": best.passed,
                "gate_records": gate_records,
                "gate_features": {
                    "mean_entropy": mean_entropy,
                    "mean_retrieval": mean_retrieval,
                    "max_prior_score": max((prior.score for prior in priors if prior is not None), default=0.0),
                    "num_supports": len(supports),
                    "num_candidates": len(all_candidates),
                },
                "structure_fidelity": fidelity,
                "retrieval_scores": retrieval_scores,
            }
        )

    pass_rate = sum(1 for row in episode_results if row["passed"]) / max(len(episode_results), 1)
    return {
        "config": config,
        "num_episodes": len(episode_results),
        "pass_rate": pass_rate,
        "episodes": episode_results,
    }


def allocate_candidate_budget(num_variants: int, candidate_budget: int, default_per_variant: int) -> List[int]:
    if num_variants <= 0:
        return []
    if candidate_budget <= 0:
        return [default_per_variant for _ in range(num_variants)]
    base = candidate_budget // num_variants
    remainder = candidate_budget % num_variants
    counts = []
    for index in range(num_variants):
        counts.append(base + (1 if index < remainder else 0))
    return counts


def structure_fidelity(query_structure: Dict[str, object], priors: List[object]) -> float:
    if not priors or priors == [None]:
        return 0.0
    best = 0.0
    query_api = set(query_structure.get("api_calls", []))
    query_flow = set(query_structure.get("control_flow", []))
    query_ds = set(query_structure.get("data_structures", []))
    for prior in priors:
        if prior is None:
            continue
        summary = prior.summary
        prior_api = set(summary.get("api_calls", []))
        prior_flow = set(summary.get("control_flow", []))
        prior_ds = set(summary.get("data_structures", []))
        overlaps = [
            overlap_ratio(query_api, prior_api),
            overlap_ratio(query_flow, prior_flow),
            overlap_ratio(query_ds, prior_ds),
        ]
        best = max(best, sum(overlaps) / len(overlaps))
    return best


def overlap_ratio(a: set, b: set) -> float:
    if not a:
        return 0.0
    return len(a & b) / len(a)


def build_oracle_prior(query: Example) -> PriorCandidate:
    summary = extract_structure(query.code).to_dict()
    summary["algorithm_plan"] = build_algorithm_plan(query.code)
    return PriorCandidate(name="oracle", score=1.0, summary=summary)


def build_random_priors(pool: List[Example], rng: random.Random, num_candidates: int) -> List[PriorCandidate]:
    if not pool:
        return []
    sampled = rng.sample(pool, k=min(num_candidates, len(pool)))
    priors = []
    for index, example in enumerate(sampled, start=1):
        priors.append(
            PriorCandidate(
                name=f"random_{index}",
                score=0.0,
                summary=summary_with_algorithm_plan(example.code),
            )
        )
    return priors


def build_weak_prior(counts: Dict[str, object]) -> PriorCandidate:
    api_counter = counts.get("api_calls")
    flow_counter = counts.get("control_flow")
    ds_counter = counts.get("data_structures")
    signature_counter = counts.get("signature")
    summary = {
        "ast_skeleton": [],
        "api_calls": [name for name, _ in api_counter.most_common(2)] if api_counter else [],
        "control_flow": [name for name, _ in flow_counter.most_common(2)] if flow_counter else [],
        "data_structures": [name for name, _ in ds_counter.most_common(2)] if ds_counter else [],
        "signature": {"num_args": signature_counter.most_common(1)[0][0] if signature_counter else None},
        "algorithm_plan": [],
    }
    return PriorCandidate(name="weak", score=0.25, summary=summary)


def corrupt_prior(prior: PriorCandidate, pool: List[Example], rng: random.Random) -> PriorCandidate:
    if not pool:
        return prior
    sampled = rng.choice(pool)
    sampled_summary = summary_with_algorithm_plan(sampled.code)
    base = dict(prior.summary)
    corrupted = {
        "ast_skeleton": sampled_summary.get("ast_skeleton", []),
        "api_calls": list(reversed(base.get("api_calls", [])))[: max(1, len(base.get("api_calls", [])))],
        "control_flow": sampled_summary.get("control_flow", []),
        "data_structures": sampled_summary.get("data_structures", []),
        "signature": sampled_summary.get("signature", {}),
        "algorithm_plan": sampled_summary.get("algorithm_plan", []),
    }
    return PriorCandidate(name="corrupted", score=0.0, summary=corrupted)


def degrade_priors(
    priors: List[PriorCandidate | None],
    pool: List[Example],
    rng: random.Random,
    mode: str,
) -> List[PriorCandidate | None]:
    degraded: List[PriorCandidate | None] = []
    for prior in priors:
        if prior is None:
            degraded.append(None)
            continue
        summary = copy.deepcopy(prior.summary)
        if mode == "drop_api_tags":
            summary["api_calls"] = []
        elif mode == "drop_control_flow_tags":
            summary["control_flow"] = []
        elif mode == "drop_data_structure_tags":
            summary["data_structures"] = []
        elif mode.startswith("replace_"):
            fraction = float(mode.split("_", 1)[1]) / 100.0
            summary = replace_structural_tags(summary, pool, rng, fraction)
        else:
            raise ValueError(f"Unknown prior_degradation mode: {mode}")
        degraded.append(
            PriorCandidate(
                name=f"{prior.name}_{mode}",
                score=prior.score,
                summary=summary,
            )
        )
    return degraded


def replace_structural_tags(
    summary: Dict[str, object],
    pool: List[Example],
    rng: random.Random,
    fraction: float,
) -> Dict[str, object]:
    if not pool:
        return summary
    replacement_summary = summary_with_algorithm_plan(rng.choice(pool).code)
    for channel in ("api_calls", "control_flow", "data_structures", "ast_skeleton"):
        values = list(summary.get(channel, []))
        if not values:
            continue
        replacement_values = list(replacement_summary.get(channel, []))
        if not replacement_values:
            continue
        replace_n = max(1, min(len(values), round(len(values) * fraction)))
        for index in rng.sample(range(len(values)), k=replace_n):
            values[index] = rng.choice(replacement_values)
        summary[channel] = values
    return summary


def summary_with_algorithm_plan(code: str) -> Dict[str, object]:
    summary = extract_structure(code).to_dict()
    summary["algorithm_plan"] = build_algorithm_plan(code)
    return summary


def build_algorithm_plan(code: str, max_steps: int = 10) -> List[str]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(code)
    except SyntaxError:
        return []
    function = next((node for node in tree.body if isinstance(node, ast.FunctionDef)), None)
    if function is None:
        return []
    steps: List[str] = []
    for stmt in function.body:
        steps.extend(statement_plan(stmt, depth=0))
        if len(steps) >= max_steps:
            break
    return steps[:max_steps]


def statement_plan(stmt: ast.stmt, depth: int) -> List[str]:
    indent = "  " * depth
    if isinstance(stmt, ast.Assign):
        targets = ", ".join(safe_unparse(target) for target in stmt.targets)
        return [f"{indent}set {targets} = {safe_unparse(stmt.value)}"]
    if isinstance(stmt, ast.AugAssign):
        return [f"{indent}update {safe_unparse(stmt.target)} {type(stmt.op).__name__}= {safe_unparse(stmt.value)}"]
    if isinstance(stmt, ast.For):
        lines = [f"{indent}loop {safe_unparse(stmt.target)} over {safe_unparse(stmt.iter)}"]
        for child in stmt.body[:3]:
            lines.extend(statement_plan(child, depth + 1))
        return lines
    if isinstance(stmt, ast.While):
        lines = [f"{indent}while {safe_unparse(stmt.test)}"]
        for child in stmt.body[:3]:
            lines.extend(statement_plan(child, depth + 1))
        return lines
    if isinstance(stmt, ast.If):
        lines = [f"{indent}if {safe_unparse(stmt.test)}"]
        for child in stmt.body[:3]:
            lines.extend(statement_plan(child, depth + 1))
        if stmt.orelse:
            lines.append(f"{indent}else")
            for child in stmt.orelse[:2]:
                lines.extend(statement_plan(child, depth + 1))
        return lines
    if isinstance(stmt, ast.Return):
        return [f"{indent}return {safe_unparse(stmt.value)}"]
    if isinstance(stmt, ast.Expr):
        return [f"{indent}evaluate {safe_unparse(stmt.value)}"]
    return [f"{indent}{type(stmt).__name__.lower()}"]


def safe_unparse(node: ast.AST | None, max_len: int = 120) -> str:
    if node is None:
        return ""
    try:
        text = ast.unparse(node)
    except Exception:
        text = type(node).__name__
    text = " ".join(text.split())
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text
