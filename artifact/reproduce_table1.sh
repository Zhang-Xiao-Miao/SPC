#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" -S scripts/61_make_conclusion_shift_table.py
printf '[PASS] regenerated conclusion-shift table\n'
