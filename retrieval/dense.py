from __future__ import annotations

import ast
import warnings
from functools import lru_cache
from typing import List, Tuple

from plan_b.schema import Example
from retrieval.common import jaccard, rank_scores, tokenize


@lru_cache(maxsize=4096)
def _dense_features(prompt: str, code: str) -> tuple[str, ...]:
    tokens = tokenize(prompt)
    feature_set = set(tokens)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(code)
        for node in ast.walk(tree):
            feature_set.add(type(node).__name__.lower())
    except SyntaxError:
        pass
    return tuple(sorted(feature_set))


def retrieve(query: Example, pool: List[Example], k: int) -> List[Tuple[float, Example]]:
    query_features = _dense_features(query.prompt, query.code)
    scored = []
    for example in pool:
        scored.append((jaccard(query_features, _dense_features(example.prompt, example.code)), example))
    return rank_scores(scored, k)
