#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/61_make_conclusion_shift_table.py
printf '[PASS] regenerated conclusion-shift table\n'
python scripts/58_make_stats_and_cost.py
printf '[PASS] regenerated stats/cost table\n'
python scripts/65_make_budget_sweep_v2.py
printf '[PASS] regenerated budget sweep support\n'
python scripts/66_make_bad_prior_breakdown.py
printf '[PASS] regenerated bad-prior breakdown\n'
python scripts/67_make_prior_quality_audit.py
printf '[PASS] regenerated prior-quality audit\n'
python scripts/69_run_controlled_degradation_sweep.py --cached-only --max-episodes 50 --candidate-budget 8 --seed 1 --generator-backend vllm_openai --model-name deepseek-ai/deepseek-coder-6.7b-instruct --api-base http://127.0.0.1:8001/v1 --device cuda --result-prefix mbppplus50_deepseek_degradation --out results/degradation_sweep/summary_deepseek_seed1_n50.json --paper-out paper/tbl_controlled_degradation_sweep.md
printf '[PASS] regenerated controlled-degradation table from cached outputs\n'
printf '[PASS] regenerated main reviewer-facing tables and figures from cached results\n'
