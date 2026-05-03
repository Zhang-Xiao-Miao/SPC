from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, List, Sequence, Tuple

from plan_b.schema import Example
from retrieval import syntax_aware
from structure.extract_ast import extract_structure


def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z_]+", text.lower())


def jaccard(a: Sequence[str], b: Sequence[str]) -> float:
    left = set(a)
    right = set(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def multiset_overlap(a: Sequence[str], b: Sequence[str]) -> float:
    left = Counter(a)
    right = Counter(b)
    if not left or not right:
        return 0.0
    shared = sum(min(left[token], right[token]) for token in left)
    total = sum(left.values()) + sum(right.values())
    return (2.0 * shared) / max(total, 1)


def build_pair_features(query: Example, support: Example, base_score: float) -> List[float]:
    query_prompt_tokens = tokenize(query.prompt)
    support_prompt_tokens = tokenize(support.prompt)
    query_code_tokens = tokenize(query.code)
    support_code_tokens = tokenize(support.code)
    query_structure = extract_structure(query.code)
    support_structure = extract_structure(support.code)
    return [
        float(base_score),
        jaccard(query_prompt_tokens, support_prompt_tokens),
        multiset_overlap(query_prompt_tokens, support_prompt_tokens),
        jaccard(query_code_tokens, support_code_tokens),
        jaccard(query_structure.api_calls, support_structure.api_calls),
        jaccard(query_structure.control_flow, support_structure.control_flow),
        jaccard(query_structure.data_structures, support_structure.data_structures),
        float(len(query.prompt)),
        float(len(support.prompt)),
        float(len(query.code)),
        float(len(support.code)),
        float(len(query.code.splitlines())),
        float(len(support.code.splitlines())),
        float(support.entry_point == query.entry_point),
        1.0 if "return" in support.code else 0.0,
        1.0 if any(tag in support_structure.control_flow for tag in {"for", "while", "if"}) else 0.0,
        1.0 if any(tag.endswith("comp") for tag in support_structure.data_structures) else 0.0,
    ]


def score_with_linear_model(features: Iterable[float], weights: Sequence[float], bias: float) -> float:
    value = bias
    for feat, weight in zip(features, weights):
        value += feat * weight
    return 1.0 / (1.0 + math.exp(-value))


def retrieve(
    query: Example,
    pool: List[Example],
    top_k: int,
    weights: Sequence[float],
    bias: float,
    preselect_k: int = 8,
) -> List[Tuple[float, Example]]:
    base = syntax_aware.retrieve(query, pool, max(top_k, preselect_k))
    rescored = []
    for base_score, support in base:
        features = build_pair_features(query, support, base_score)
        score = score_with_linear_model(features, weights, bias)
        rescored.append((score, support))
    rescored.sort(key=lambda item: item[0], reverse=True)
    return rescored[:top_k]
