from __future__ import annotations

from collections import Counter
from typing import Dict, List

from plan_b.schema import PriorCandidate


def induce_union(counts: Dict[str, Counter], top_m: int = 3) -> List[PriorCandidate]:
    prior = {
        channel: [item for item, _ in counter.most_common(top_m)]
        for channel, counter in counts.items()
    }
    return [PriorCandidate(name="union", score=1.0, summary=prior)]

