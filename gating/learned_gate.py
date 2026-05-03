from __future__ import annotations

from typing import Iterable, List, Sequence

from sklearn.linear_model import LogisticRegression


class LearnedGate:
    def __init__(self) -> None:
        self.model = LogisticRegression(max_iter=200)
        self.is_fit = False

    def fit(self, features: Sequence[Sequence[float]], labels: Sequence[int]) -> None:
        if not features:
            return
        self.model.fit(features, labels)
        self.is_fit = True

    def predict_proba(self, features: Iterable[Sequence[float]]) -> List[float]:
        features = list(features)
        if not features:
            return []
        if not self.is_fit:
            return [0.5 for _ in features]
        return self.model.predict_proba(features)[:, 1].tolist()

