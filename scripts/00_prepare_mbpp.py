from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from datasets import load_dataset

from plan_b.config import ensure_dir
from plan_b.io_utils import write_json
from plan_b.mbpp import dump_examples, materialize_tests, normalize_mbpp_record


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and normalize MBPP.")
    parser.add_argument("--output-dir", default="data/processed/mbpp", help="Target directory.")
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    dataset = load_dataset("mbpp")
    summary = {}
    for split_name, split in dataset.items():
        examples = [normalize_mbpp_record(row, split_name, index) for index, row in enumerate(split)]
        dump_examples(output_dir / f"{split_name}.jsonl", examples)
        materialize_tests(output_dir / "tests" / split_name, examples)
        summary[split_name] = len(examples)
    write_json(output_dir / "summary.json", summary)


if __name__ == "__main__":
    main()
