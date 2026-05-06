#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
if command -v timeout >/dev/null 2>&1; then
  timeout 60 "$PYTHON_BIN" -S scripts/71_run_pipeline_smoke_test.py
else
  echo "[WARN] timeout command not found; running smoke test without timeout"
  "$PYTHON_BIN" -S scripts/71_run_pipeline_smoke_test.py
fi
