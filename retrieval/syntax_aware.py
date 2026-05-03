from __future__ import annotations

import ast
import warnings
from functools import lru_cache
from typing import List, Tuple

from plan_b.schema import Example
from retrieval.common import jaccard, rank_scores, tokenize


@lru_cache(maxsize=4096)
def _syntax_signature(prompt: str, code: str) -> tuple[str, ...]:
    signature = set(tokenize(prompt))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    signature.add(f"call:{node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    signature.add(f"call:{node.func.attr}")
            elif isinstance(node, (ast.For, ast.While, ast.If, ast.Try, ast.ListComp, ast.DictComp, ast.SetComp)):
                signature.add(type(node).__name__.lower())
    except SyntaxError:
        pass
    return tuple(sorted(signature))


def retrieve(query: Example, pool: List[Example], k: int) -> List[Tuple[float, Example]]:
    query_signature = _syntax_signature(query.prompt, query.code)
    scored = []
    for example in pool:
        scored.append((jaccard(query_signature, _syntax_signature(example.prompt, example.code)), example))
    return rank_scores(scored, k)
