#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/72_check_live_rerun_prereqs.py "$@"
