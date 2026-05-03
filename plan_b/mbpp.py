from __future__ import annotations

import ast
from pathlib import Path
from typing import List

from plan_b.io_utils import read_jsonl, write_jsonl, write_text
from plan_b.schema import Example


def normalize_mbpp_record(row: dict, split: str, index: int) -> Example:
    prompt = row.get("text") or row.get("prompt") or ""
    code = row.get("code") or row.get("canonical_solution") or ""
    tests = row.get("test_list") or row.get("test") or []
    entry_point = row.get("entry_point") or infer_entry_point(code) or f"solution_{index}"
    if isinstance(tests, list):
        test_body = "\n".join(tests)
    else:
        test_body = str(tests)
    task_id = row.get("task_id") or row.get("name") or f"mbpp_{split}_{index:04d}"
    metadata = {
        "raw_task_id": row.get("task_id"),
        "source_prompt": row.get("prompt"),
    }
    return Example(
        task_id=task_id,
        prompt=prompt,
        code=code,
        test=test_body,
        entry_point=entry_point,
        split=split,
        metadata=metadata,
    )


def infer_entry_point(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return node.name
    return None


def dump_examples(path: str | Path, examples: List[Example]) -> None:
    rows = [example.to_dict() for example in examples]
    write_jsonl(path, rows)


def materialize_tests(base_dir: str | Path, examples: List[Example]) -> None:
    target_dir = Path(base_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    for example in examples:
        write_text(target_dir / f"{example.task_id}.py", example.test)


def load_examples(path: str | Path) -> List[Example]:
    rows = read_jsonl(path)
    return [Example(**row) for row in rows]

