from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Iterable, List, Tuple

from plan_b.schema import Example
from retrieval.common import cosine_counter, jaccard, rank_scores, tokenize
from structure.extract_ast import extract_structure


LEXICAL_WEIGHT = 0.45
PROMPT_INTENT_WEIGHT = 0.20
STRUCTURAL_MATCH_WEIGHT = 0.35


def _text(example: Example) -> str:
    return f"{example.prompt}\n{example.entry_point}"


def _has_any(tokens: set[str], names: Iterable[str]) -> bool:
    return any(name in tokens for name in names)


@lru_cache(maxsize=4096)
def _prompt_intent_tags(text: str) -> tuple[str, ...]:
    tokens = set(tokenize(text))
    tags: set[str] = set()

    if _has_any(tokens, ["string", "strings", "substring", "character", "characters", "word", "words"]):
        tags.add("domain:string")
        tags.add("data:string")
    if _has_any(tokens, ["list", "lists", "array", "arrays", "sequence", "sequences"]):
        tags.add("domain:sequence")
        tags.add("data:list")
    if _has_any(tokens, ["matrix", "matrices", "row", "rows", "column", "columns"]):
        tags.add("domain:matrix")
        tags.add("data:list")
        tags.add("flow:nested_loop")
    if _has_any(tokens, ["dictionary", "dict", "map", "mapping"]):
        tags.add("data:dict")
    if _has_any(tokens, ["set", "sets", "unique", "distinct", "duplicate", "duplicates"]):
        tags.add("data:set")
    if _has_any(tokens, ["tuple", "tuples", "pair", "pairs"]):
        tags.add("data:tuple")

    if _has_any(tokens, ["sort", "sorted", "ascending", "descending", "order", "ordered"]):
        tags.add("op:sort")
        tags.add("api:sorted")
    if _has_any(tokens, ["count", "counts", "frequency", "frequencies", "occurrence", "occurrences", "common"]):
        tags.add("op:count")
        tags.add("data:dict")
    if _has_any(tokens, ["find", "search", "contains", "check", "whether", "true", "false"]):
        tags.add("op:predicate")
        tags.add("flow:if")
    if _has_any(tokens, ["remove", "delete", "filter", "replace", "split"]):
        tags.add("op:transform")
        tags.add("flow:if")
    if _has_any(tokens, ["maximum", "minimum", "largest", "smallest", "longest", "shortest", "sum"]):
        tags.add("op:aggregate")
    if _has_any(tokens, ["prime", "factor", "factors", "divisible", "divisor", "gcd", "lcm"]):
        tags.add("domain:number_theory")
        tags.add("flow:loop")
    if _has_any(tokens, ["fibonacci", "recursive", "recursion", "factorial"]):
        tags.add("op:recursion")
    if _has_any(tokens, ["regex", "regular", "pattern", "lowercase", "uppercase"]):
        tags.add("api:re")

    return tuple(sorted(tags))


@lru_cache(maxsize=4096)
def _support_structural_tags_from_fields(prompt: str, entry_point: str, code: str) -> tuple[str, ...]:
    summary = extract_structure(code)
    tags: set[str] = set(_prompt_intent_tags(f"{prompt}\n{entry_point}"))
    tags.update(f"api:{name}" for name in summary.api_calls)
    tags.update(f"flow:{name}" for name in summary.control_flow)
    tags.update(f"data:{name}" for name in summary.data_structures)
    for node in summary.ast_skeleton:
        if node == "For":
            tags.add("flow:loop")
        elif node == "While":
            tags.add("flow:loop")
        elif node == "If":
            tags.add("flow:if")
        elif node in {"ListComp", "DictComp", "SetComp"}:
            tags.add("flow:comprehension")
    num_args = summary.signature.get("num_args")
    if num_args is not None:
        tags.add(f"sig_args:{num_args}")
    return tuple(sorted(tags))


def _support_structural_tags(example: Example) -> tuple[str, ...]:
    return _support_structural_tags_from_fields(example.prompt, example.entry_point, example.code)


def retrieve(query: Example, pool: List[Example], k: int) -> List[Tuple[float, Example]]:
    query_text = _text(query)
    query_counter = Counter(tokenize(query_text))
    query_intent = _prompt_intent_tags(query_text)

    scored = []
    for example in pool:
        support_text = _text(example)
        lexical = cosine_counter(query_counter, Counter(tokenize(support_text)))
        prompt_intent = jaccard(query_intent, _prompt_intent_tags(support_text))
        structural = jaccard(query_intent, _support_structural_tags(example))
        score = (
            LEXICAL_WEIGHT * lexical
            + PROMPT_INTENT_WEIGHT * prompt_intent
            + STRUCTURAL_MATCH_WEIGHT * structural
        )
        scored.append((score, example))
    return rank_scores(scored, k)
