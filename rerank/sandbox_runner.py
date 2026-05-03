from __future__ import annotations

import json
import os
import resource
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict


def _limit_resources(memory_mb: int, timeout_sec: int) -> None:
    memory_bytes = memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (timeout_sec, timeout_sec + 1))
    os.environ["PYTHONNOUSERSITE"] = "1"


def run_candidate(code: str, tests: str, timeout_sec: int = 5, memory_mb: int = 512) -> Dict[str, object]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = Path(tmp_dir) / "candidate_eval.py"
        payload = code.rstrip() + "\n\n" + tests.rstrip() + "\n"
        script_path.write_text(payload, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                preexec_fn=lambda: _limit_resources(memory_mb, timeout_sec),
            )
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "passed": False, "stdout": "", "stderr": "timeout"}
        status = "passed" if completed.returncode == 0 else "failed"
        return {
            "status": status,
            "passed": completed.returncode == 0,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
            "returncode": completed.returncode,
        }
