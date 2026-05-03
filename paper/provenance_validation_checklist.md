# Provenance Validation Checklist

This checklist is the reviewer-facing path for the two provenance risks raised in review 6: prompt-only matcher tuning and prior-quality audit post-hoc interpretation. It is an artifact validation aid, not a new experiment.

## Prompt-Only Matcher Provenance

Required evidence:

- Code path: `retrieval/prompt_structural.py`.
- Documentation path: `paper/prompt_only_structural_matcher.md`.
- Pre-run plan path: `paperB/prompt_only_structural_control_plan.md`.
- Query-side access is task prompt plus entry point only.
- The matcher does not use query solution code, tests, generated candidates, execution feedback, or outcome labels.
- The fixed score is `0.45 * lexical_cosine + 0.20 * prompt_intent_jaccard + 0.35 * structural_tag_jaccard`.
- The same implementation is used for the `MBPP+100` prompt-only structural slice and the full `MBPP+224` prompt-only structural rerun.
- The reported full `MBPP+224` rerun is not selected from an alternative-weight sweep, and no alternative-weight sweep is part of the canonical artifact.

Reviewer check:

```bash
python - <<'PY'
from pathlib import Path
p = Path("retrieval/prompt_structural.py").read_text()
required = [
    "LEXICAL_WEIGHT = 0.45",
    "PROMPT_INTENT_WEIGHT = 0.20",
    "STRUCTURAL_MATCH_WEIGHT = 0.35",
    "query_text = _text(query)",
]
for token in required:
    assert token in p, token
retrieve_body = p.split("def retrieve(", 1)[1]
assert "query.code" not in retrieve_body
assert "query.tests" not in retrieve_body
print("prompt_structural matcher provenance checks passed")
PY
```

## Prior-Quality Audit Provenance

Required evidence:

- `structure_fidelity` is emitted by `plan_b/pipeline.py` before paper-facing audit tables are generated.
- The field appears in packaged raw-result JSON files under `results/mbpp224_fair_budget/` and `results/prompt_only_structural_mbpp224_fair_budget/`.
- `scripts/67_make_prior_quality_audit.py` reads stored raw-result fields and does not recompute retrieval, rerun generation, tune prompts, tune retrieval, filter episodes, or compute new `structure_fidelity` values for the paper table.
- The audit reports all relevant conditions: code-aware `single_prior`, `multi_prior`, `random_prior`, `corrupted_prior`, plus full `MBPP+224` prompt-only `single_prior` and `multi_prior`.
- The complete threshold sensitivity table is in `paper/tbl_prior_quality_audit.md` and `paper/tbl_prior_quality_audit.json`.

Reviewer check:

```bash
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
print("raw structure_fidelity fields are present")
PY

python scripts/67_make_prior_quality_audit.py
```

## Table Regeneration Versus Live Rerun Boundary

Reviewer-first scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not call an LLM and do not rebuild raw generations. Full live reruns require a matching model endpoint or local model and should be run only in an isolated environment when generated Python code is executed.

Reviewer command:

```bash
bash artifact/reproduce_main.sh
```

## Release Policy Boundary

Public artifact release follows `paper/data_release_policy.md`: upstream benchmark datasets or tests are not publicly redistributed unless redistribution permission is verified. When permission is not verified, public release uses preparation scripts, provenance notes, metadata, expected directory layout, and hashes instead.
