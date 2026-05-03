from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.io_utils import write_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Create placeholder instructions for EvalPlus preparation.")
    parser.add_argument("--output", default="data/tests/README_EVALPLUS.md")
    args = parser.parse_args()
    content = (
        "# EvalPlus Preparation\n\n"
        "Install `evalplus` in the runtime that has network access, then export MBPP+ and HumanEval+ tests into `data/tests/`.\n"
        "This repository keeps the hook script separate because the public benchmark assets are large and environment-dependent.\n"
    )
    write_text(args.output, content)


if __name__ == "__main__":
    main()
