from __future__ import annotations

import math
from collections import Counter
from typing import Dict, List

from plan_b.schema import PriorCandidate


def entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    value = 0.0
    for count in counter.values():
        prob = count / total
        value -= prob * math.log(prob + 1e-12)
    return value


def gate(prior: PriorCandidate, counts: Dict[str, Counter], retrieval_scores: List[float], entropy_threshold: float = 1.2) -> Dict[str, float | bool]:
    entropies = [entropy(counter) for counter in counts.values() if counter]
    mean_entropy = sum(entropies) / len(entropies) if entropies else 0.0
    mean_retrieval = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
    decision = mean_entropy <= entropy_threshold and mean_retrieval >= 0.1 and bool(prior.summary)
    return {
        "use_prior": decision,
        "mean_entropy": mean_entropy,
        "mean_retrieval": mean_retrieval,
        "prior_score": prior.score,
    }

