#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/65_make_budget_sweep_v2.py
python scripts/66_make_bad_prior_breakdown.py
printf '[PASS] regenerated figure-support artifacts from cached results\n'
