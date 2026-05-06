#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" -S scripts/70_reviewer_claim_audit.py
