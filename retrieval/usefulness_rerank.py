from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, List, Sequence, Tuple

from plan_b.schema import Example
from retrieval import syntax_aware


def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z_]+", text.lower())


def jaccard(a: Sequence[str], b: Sequence[str]) -> float:
    left = set(a)
    right = set(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def build_pair_features(query: Example, support: Example, base_score: float) -> List[float]:
    query_tokens = tokenize(query.prompt)
    support_tokens = tokenize(support.prompt)
    query_counts = Counter(query_tokens)
    support_counts = Counter(support_tokens)
    overlap = sum(min(query_counts[token], support_counts[token]) for token in query_counts)
    return [
        float(base_score),
        jaccard(query_tokens, support_tokens),
        float(overlap),
        float(len(query_tokens)),
        float(len(support_tokens)),
        float(support.entry_point == query.entry_point),
    ]


def score_with_linear_model(features: Iterable[float], weights: Sequence[float], bias: float) -> float:
    value = bias
    for feat, weight in zip(features, weights):
        value += feat * weight
    return 1.0 / (1.0 + math.exp(-value))


def retrieve(query: Example, pool: List[Example], top_k: int, weights: Sequence[float], bias: float, preselect_k: int = 8) -> List[Tuple[float, Example]]:
    base = syntax_aware.retrieve(query, pool, max(top_k, preselect_k))
    rescored = []
    for base_score, support in base:
        features = build_pair_features(query, support, base_score)
        score = score_with_linear_model(features, weights, bias)
        rescored.append((score, support))
    rescored.sort(key=lambda item: item[0], reverse=True)
    return rescored[:top_k]
