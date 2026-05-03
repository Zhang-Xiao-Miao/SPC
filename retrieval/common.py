from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, List, Sequence, Tuple

from plan_b.schema import Example


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")


def tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def cosine_counter(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_scores(scores: Sequence[Tuple[float, Example]], k: int) -> List[Tuple[float, Example]]:
    return sorted(scores, key=lambda item: item[0], reverse=True)[:k]

