from __future__ import annotations

from collections import Counter
from typing import Dict, List

from plan_b.schema import PriorCandidate


def induce_vote(counts: Dict[str, Counter], top_m: int = 3) -> List[PriorCandidate]:
    candidates: List[PriorCandidate] = []
    for rank in range(top_m):
        summary = {}
        score = 0.0
        for channel, counter in counts.items():
            items = counter.most_common(top_m)
            summary[channel] = [items[rank][0]] if rank < len(items) else []
            if rank < len(items):
                score += float(items[rank][1])
        candidates.append(PriorCandidate(name=f"vote_{rank + 1}", score=score, summary=summary))
    return candidates

