from __future__ import annotations

import gzip
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from plan_b.io_utils import write_jsonl, write_text
from plan_b.schema import Example

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def load_evalplus_rows(path: str | Path) -> List[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_examples_from_evalplus(
    rows: Iterable[dict],
    split: str,
    dataset_name: str,
    include_ids: set[str] | None = None,
) -> List[Example]:
    examples: List[Example] = []
    for row in rows:
        raw_id = row["task_id"].split("/")[-1]
        if include_ids is not None and raw_id not in include_ids:
            continue
        task_id = f"{dataset_name.lower()}_{raw_id}"
        canonical = normalize_canonical_solution(row["prompt"], row["canonical_solution"])
        test_code = build_evalplus_test_code(canonical, row["entry_point"], row["base_input"], row["plus_input"], row.get("atol", 0.0))
        examples.append(
            Example(
                task_id=task_id,
                prompt=row["prompt"],
                code=canonical,
                test=test_code,
                entry_point=row["entry_point"],
                split=split,
                metadata={"raw_task_id": row["task_id"], "dataset": dataset_name},
            )
        )
    return examples


def normalize_canonical_solution(prompt: str, canonical_solution: str) -> str:
    prompt = prompt.rstrip() + "\n"
    solution = canonical_solution.strip("\n")
    return prompt + solution + "\n"


def build_evalplus_test_code(
    canonical_solution: str,
    entry_point: str,
    base_inputs: list,
    plus_inputs: list,
    atol: float | int | None,
) -> str:
    all_inputs = list(base_inputs) + list(plus_inputs)
    expected = compute_expected_outputs(canonical_solution, entry_point, all_inputs)
    lines = [
        "import math",
        "from collections.abc import Mapping, Sequence, Set",
        "",
        "def _normalize_value(value):",
        "    if isinstance(value, tuple):",
        "        return tuple(_normalize_value(v) for v in value)",
        "    if isinstance(value, list):",
        "        return [_normalize_value(v) for v in value]",
        "    if isinstance(value, set):",
        "        return sorted(_normalize_value(v) for v in value)",
        "    if isinstance(value, dict):",
        "        return {k: _normalize_value(v) for k, v in sorted(value.items(), key=lambda item: repr(item[0]))}",
        "    return value",
        "",
        "def _assert_close(actual, expected, atol):",
        "    if isinstance(expected, float):",
        "        assert math.isclose(actual, expected, rel_tol=1e-7, abs_tol=atol)",
        "        return",
        "    if isinstance(expected, list):",
        "        assert len(actual) == len(expected)",
        "        for act_item, exp_item in zip(actual, expected):",
        "            _assert_close(act_item, exp_item, atol)",
        "        return",
        "    if isinstance(expected, tuple):",
        "        assert len(actual) == len(expected)",
        "        for act_item, exp_item in zip(actual, expected):",
        "            _assert_close(act_item, exp_item, atol)",
        "        return",
        "    if isinstance(expected, dict):",
        "        assert set(actual.keys()) == set(expected.keys())",
        "        for key in expected:",
        "            _assert_close(actual[key], expected[key], atol)",
        "        return",
        "    assert _normalize_value(actual) == _normalize_value(expected)",
        "",
    ]
    tol = float(atol or 0.0)
    for index, (args, exp) in enumerate(zip(all_inputs, expected)):
        args_repr = repr(tuple(args))
        lines.append(f"_args_{index} = {args_repr}")
        if isinstance(exp, dict) and "__exception__" in exp:
            lines.append("try:")
            lines.append(f"    {entry_point}(*_args_{index})")
            lines.append("except Exception as exc:")
            lines.append(f"    assert type(exc).__name__ == {exp['__exception__']!r}")
            lines.append("else:")
            lines.append("    raise AssertionError('expected exception was not raised')")
        else:
            exp_repr = repr(exp)
            lines.append(f"_expected_{index} = {exp_repr}")
            lines.append(f"_actual_{index} = {entry_point}(*_args_{index})")
            lines.append(f"_assert_close(_actual_{index}, _expected_{index}, {tol!r})")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def compute_expected_outputs(canonical_solution: str, entry_point: str, all_inputs: list) -> List[Any]:
    namespace: Dict[str, Any] = {}
    exec(canonical_solution, namespace, namespace)
    function = namespace[entry_point]
    outputs = []
    for args in all_inputs:
        try:
            outputs.append(function(*args))
        except Exception as exc:
            outputs.append({"__exception__": type(exc).__name__})
    return outputs


def dump_examples(path: str | Path, tests_dir: str | Path, examples: List[Example]) -> None:
    write_jsonl(path, [example.to_dict() for example in examples])
    tests_root = Path(tests_dir)
    tests_root.mkdir(parents=True, exist_ok=True)
    for example in examples:
        write_text(tests_root / f"{example.task_id}.py", example.test)
