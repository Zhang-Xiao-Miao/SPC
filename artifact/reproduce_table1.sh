#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/61_make_conclusion_shift_table.py
printf '[PASS] regenerated conclusion-shift table\n'
