from __future__ import annotations

from typing import Iterable, List, Sequence


def expected_calibration_error(probs: Sequence[float], labels: Sequence[int], num_bins: int = 10) -> float:
    if not probs:
        return 0.0
    buckets = [[] for _ in range(num_bins)]
    for prob, label in zip(probs, labels):
        index = min(int(prob * num_bins), num_bins - 1)
        buckets[index].append((prob, label))
    total = len(probs)
    ece = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        mean_prob = sum(prob for prob, _ in bucket) / len(bucket)
        mean_label = sum(label for _, label in bucket) / len(bucket)
        ece += abs(mean_prob - mean_label) * len(bucket) / total
    return ece


def brier_score(probs: Iterable[float], labels: Iterable[int]) -> float:
    probs = list(probs)
    labels = list(labels)
    if not probs:
        return 0.0
    return sum((p - y) ** 2 for p, y in zip(probs, labels)) / len(probs)

