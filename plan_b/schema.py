from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Example:
    task_id: str
    prompt: str
    code: str
    test: str
    entry_point: str
    split: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Episode:
    episode_id: str
    query_id: str
    k: int
    retrieval_mode: str
    support_ids: List[str]
    query_prompt: str
    tests_path: str
    entry_point: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StructureSummary:
    ast_skeleton: List[str]
    api_calls: List[str]
    control_flow: List[str]
    data_structures: List[str]
    signature: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PriorCandidate:
    name: str
    score: float
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GenerationCandidate:
    code: str
    source: str
    prior_name: Optional[str]
    score: float = 0.0
    compile_ok: Optional[bool] = None
    exec_status: Optional[str] = None
    passed: Optional[bool] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

