from __future__ import annotations

import argparse
import ast
import importlib.util
import os
import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from datasets import Dataset

from plan_b.io_utils import write_jsonl, write_text
from plan_b.schema import Episode, Example
from plan_b.mbpp import load_examples
from retrieval import syntax_aware


DEFAULT_HARD_ARROW_PATH = Path(os.environ.get("BIGCODEBENCH_HARD_ARROW", "data/upstream/bigcodebench-hard-v0.1.4.arrow"))


def is_module_available(name: str) -> bool:
    root = name.split(".")[0]
    return root in sys.stdlib_module_names or importlib.util.find_spec(root) is not None


def row_libs(row: dict) -> List[str]:
    libs = row.get("libs") or []
    if isinstance(libs, str):
        libs = ast.literal_eval(libs)
    return [lib.split(".")[0] for lib in libs]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a dependency-compatible BigCodeBench-Hard slice for Plan B.")
    parser.add_argument("--max-tasks", type=int, default=20)
    parser.add_argument("--source-arrow", default=str(DEFAULT_HARD_ARROW_PATH))
    parser.add_argument("--out-examples", default="data/processed/bigcodebench_hard_compatible20.jsonl")
    parser.add_argument("--out-episodes", default="data/episodes/bigcodebench_hard_compatible20_syntax_episodes.jsonl")
    parser.add_argument("--paper-out", default="paper/tbl_external_modern_sampling.md")
    args = parser.parse_args()

    source_arrow = Path(args.source_arrow)
    if not source_arrow.exists():
        raise FileNotFoundError(
            f"BigCodeBench-Hard source arrow not found at {source_arrow}. "
            "Use --source-arrow to point at a local dataset cache, or rely on the already-packaged "
            "processed compatibility slices under data/processed/ and data/episodes/."
        )

    ds = Dataset.from_file(str(source_arrow))
    train_examples = load_examples("data/processed/mbpp/train.jsonl")

    examples: List[Example] = []
    episodes = []
    rows = []
    for row in ds:
        libs = row_libs(row)
        if not all(is_module_available(lib) for lib in libs):
            continue
        example = Example(
            task_id=row["task_id"].replace("/", "_").lower(),
            prompt=row["instruct_prompt"],
            code=row["canonical_solution"],
            test=row["test"],
            entry_point=row["entry_point"],
            split="test",
            metadata={
                "source_dataset": "bigcodebench-hard",
                "source_version": "v0.1.4",
                "raw_task_id": row["task_id"],
                "libs": libs,
            },
        )
        supports = syntax_aware.retrieve(example, train_examples, 1)
        episodes.append(
            Episode(
                episode_id=f"{example.task_id}_k1_syntax_aware",
                query_id=example.task_id,
                k=1,
                retrieval_mode="syntax_aware",
                support_ids=[support.task_id for _, support in supports[:1]],
                query_prompt=example.prompt,
                tests_path="",
                entry_point=example.entry_point,
            ).to_dict()
        )
        examples.append(example)
        rows.append([example.task_id, ",".join(libs), supports[0][1].task_id if supports else ""])
        if len(examples) >= args.max_tasks:
            break

    write_jsonl(args.out_examples, [example.to_dict() for example in examples])
    write_jsonl(args.out_episodes, episodes)

    md = "# Modern External Slice Sampling\n\n"
    md += "- Dataset: `BigCodeBench-Hard v0.1.4`\n"
    md += f"- Slice size: `{len(examples)}`\n"
    md += "- Selection rule: keep tasks whose declared dependency roots are importable in the current environment; then take the first compatible tasks in dataset order.\n"
    md += "- Retrieval support pool: `MBPP train`\n"
    md += "- Caveat: this is a compatibility-filtered slice, not a random sample of the full benchmark.\n"
    md += f"- Source arrow: `{source_arrow}`\n\n"
    md += "| Task | Dependency Roots | Retrieved Support |\n"
    md += "| --- | --- | --- |\n"
    for task_id, libs, support_id in rows:
        md += f"| {task_id} | {libs} | {support_id} |\n"
    write_text(args.paper_out, md)


if __name__ == "__main__":
    main()
