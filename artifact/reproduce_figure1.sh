#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/65_make_budget_sweep_v2.py
printf '[PASS] regenerated budget sweep support\n'
