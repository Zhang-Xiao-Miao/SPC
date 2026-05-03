#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1

python - <<'PY'
from pathlib import Path

source = Path("retrieval/prompt_structural.py").read_text()
required_tokens = [
    "LEXICAL_WEIGHT = 0.45",
    "PROMPT_INTENT_WEIGHT = 0.20",
    "STRUCTURAL_MATCH_WEIGHT = 0.35",
    "query_text = _text(query)",
]
for token in required_tokens:
    assert token in source, token

retrieve_body = source.split("def retrieve(", 1)[1]
for forbidden in ["query.code", "query.tests", "execution", "passed"]:
    assert forbidden not in retrieve_body, forbidden

print("[PASS] prompt_structural matcher constants verified")
print("[PASS] query-side prompt-only access boundary verified")
PY

python - <<'PY'
from plan_b.io_utils import read_json

paths = [
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/prompt_only_structural_mbpp224_fair_budget/mbppplus224_prompt_structural_multi_prior_mbrexec_budget8_seed1.json",
]
for path in paths:
    payload = read_json(path)
    assert "episodes" in payload and payload["episodes"], path
    assert "structure_fidelity" in payload["episodes"][0], path

print("[PASS] raw structure_fidelity fields verified")
PY

python scripts/67_make_prior_quality_audit.py
test -s paper/tbl_prior_quality_response.md
test -s paper/fig_prior_quality_response.md
printf '[PASS] prior-quality response regenerated from cached outputs\n'
printf '[PASS] verified matcher provenance and regenerated prior-quality audit from cached outputs\n'
