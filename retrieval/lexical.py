from __future__ import annotations

from collections import Counter
from typing import List, Tuple

from plan_b.schema import Example
from retrieval.common import cosine_counter, rank_scores, tokenize


def retrieve(query: Example, pool: List[Example], k: int) -> List[Tuple[float, Example]]:
    query_counter = Counter(tokenize(query.prompt))
    scored = []
    for example in pool:
        counter = Counter(tokenize(example.prompt))
        scored.append((cosine_counter(query_counter, counter), example))
    return rank_scores(scored, k)

