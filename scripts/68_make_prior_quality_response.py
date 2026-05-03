from __future__ import annotations

import subprocess
import sys


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/67_make_prior_quality_audit.py",
            "--out-json",
            "paper/tbl_prior_quality_audit.json",
            "--out-md",
            "paper/tbl_prior_quality_audit.md",
            "--out-response-json",
            "paper/tbl_prior_quality_response.json",
            "--out-response-md",
            "paper/tbl_prior_quality_response.md",
            "--out-fig-md",
            "paper/fig_prior_quality_response.md",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
