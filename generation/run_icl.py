from __future__ import annotations

import argparse
from pathlib import Path

from plan_b.config import load_config
from plan_b.io_utils import write_json
from plan_b.mbpp import load_examples
from plan_b.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Plan B ICL baseline.")
    parser.add_argument("--config", required=True, help="Path to yaml config.")
    args = parser.parse_args()
    config = load_config(args.config)
    result = run_pipeline(config)
    write_json(config["result_path"], result)


if __name__ == "__main__":
    main()

