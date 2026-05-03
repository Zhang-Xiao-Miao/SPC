from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.io_utils import write_jsonl
from plan_b.mbpp import load_examples
from plan_b.schema import Episode
from retrieval import dense as dense_retrieval
from retrieval import lexical as lexical_retrieval
from retrieval import prompt_structural as prompt_structural_retrieval
from retrieval import syntax_aware as syntax_retrieval


RETRIEVERS = {
    "lexical": lexical_retrieval.retrieve,
    "dense": dense_retrieval.retrieve,
    "prompt_structural": prompt_structural_retrieval.retrieve,
    "syntax_aware": syntax_retrieval.retrieve,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build fixed few-shot episodes.")
    parser.add_argument("--train-path", default="data/processed/mbpp/train.jsonl")
    parser.add_argument("--eval-path", default="data/processed/mbpp/test.jsonl")
    parser.add_argument("--output-path", default="data/episodes/mbpp_test_episodes.jsonl")
    parser.add_argument("--shots", nargs="+", type=int, default=[0, 1, 3, 5])
    parser.add_argument("--retrieval-modes", nargs="+", default=["lexical", "dense", "syntax_aware"])
    parser.add_argument("--limit-eval", type=int, default=0, help="Only build episodes for the first N queries.")
    args = parser.parse_args()

    train_examples = load_examples(args.train_path)
    eval_examples = load_examples(args.eval_path)
    if args.limit_eval:
        eval_examples = eval_examples[: args.limit_eval]

    rows = []
    for retrieval_mode in args.retrieval_modes:
        retriever = RETRIEVERS[retrieval_mode]
        for shot in args.shots:
            for query in eval_examples:
                supports = retriever(query, train_examples, max(shot, 1))
                support_ids = [example.task_id for _, example in supports[:shot]]
                rows.append(
                    Episode(
                        episode_id=f"{query.task_id}_k{shot}_{retrieval_mode}",
                        query_id=query.task_id,
                        k=shot,
                        retrieval_mode=retrieval_mode,
                        support_ids=support_ids,
                        query_prompt=query.prompt,
                        tests_path=f"data/processed/mbpp/tests/{query.split}/{query.task_id}.py",
                        entry_point=query.entry_point,
                    ).to_dict()
                )
    write_jsonl(args.output_path, rows)


if __name__ == "__main__":
    main()
