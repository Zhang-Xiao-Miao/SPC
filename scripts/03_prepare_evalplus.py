from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.evalplus import build_examples_from_evalplus, dump_examples, load_evalplus_rows
from plan_b.mbpp import load_examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize EvalPlus MBPP+ and HumanEval+ into repository format.")
    parser.add_argument("--mbppplus-path", default="data/raw/evalplus/MbppPlus.jsonl.gz")
    parser.add_argument("--humanevalplus-path", default="data/raw/evalplus/HumanEvalPlus.jsonl.gz")
    parser.add_argument("--output-dir", default="data/processed/evalplus")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mbpp_test = load_examples("data/processed/mbpp/test.jsonl")
    mbpp_test_ids = {str(example.task_id) for example in mbpp_test}

    mbppplus_rows = load_evalplus_rows(args.mbppplus_path)
    mbppplus_examples = build_examples_from_evalplus(
        mbppplus_rows,
        split="test",
        dataset_name="mbppplus",
        include_ids=mbpp_test_ids,
    )
    dump_examples(
        output_dir / "mbppplus_test.jsonl",
        output_dir / "tests" / "mbppplus",
        mbppplus_examples,
    )

    humanevalplus_rows = load_evalplus_rows(args.humanevalplus_path)
    humanevalplus_examples = build_examples_from_evalplus(
        humanevalplus_rows,
        split="test",
        dataset_name="humanevalplus",
    )
    dump_examples(
        output_dir / "humanevalplus_test.jsonl",
        output_dir / "tests" / "humanevalplus",
        humanevalplus_examples,
    )

    print({"mbppplus_test": len(mbppplus_examples), "humanevalplus_test": len(humanevalplus_examples)})


if __name__ == "__main__":
    main()
