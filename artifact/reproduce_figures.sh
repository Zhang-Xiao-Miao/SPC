#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" -S scripts/65_make_budget_sweep_v2.py
"$PYTHON_BIN" -S scripts/66_make_bad_prior_breakdown.py
printf '[PASS] regenerated figure-support artifacts from cached results\n'
