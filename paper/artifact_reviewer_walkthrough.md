# Reviewer-Facing Artifact Walkthrough

This note gives the shortest inspection path for the E&D artifact. It separates table regeneration from full live-model reruns.

## Reviewer Quickstart

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

These steps verify the central artifact claims without live LLM inference. They regenerate derived paper objects, check prompt-only matcher provenance, check raw `structure_fidelity` fields, regenerate the prior-quality response audit from cached outputs, and expose the supported/unsupported claim map.

For a compact overview of the contribution and artifact contract, inspect `paper/contribution_and_artifact_summary.md`. For the latest recorded verification summary, inspect `artifact/VERIFICATION_LOG_2026-04-29.md`.

For reusable versions of the reporting pattern, inspect `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, and `artifact/CLAIM_SURVIVAL_CARD.md`. For the exact reviewer package inventory and exclusions, inspect `artifact/CANONICAL_REVIEWER_PACKAGE.md`. The controlled degradation pilot and its fixed reporting boundary are in `paper/tbl_controlled_degradation_sweep.md` and `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`. Granite and StarCoder2 replicate-sensitive backend checks are in `paper/tbl_backend_replicate_boundary.md` and `paper/backend_replicate_boundary_notes.md`.

## Manual Inspection Path

1. Inspect the prompt-only matcher boundary:
   `paper/prompt_only_structural_matcher.md`
   `retrieval/prompt_structural.py`
2. Inspect the prior-quality audit provenance:
   `paper/prior_quality_audit_provenance.md`
   `scripts/67_make_prior_quality_audit.py`
   `scripts/68_make_prior_quality_response.py`
   `paper/tbl_prior_quality_audit.md`
   `paper/tbl_prior_quality_audit.json`
   `paper/tbl_prior_quality_response.md`
   `paper/tbl_prior_quality_response.json`
   `paper/fig_prior_quality_response.md`
3. Inspect the consolidated provenance checklist:
   `paper/provenance_validation_checklist.md`
4. Inspect data-release and safety boundaries:
   `paper/data_release_policy.md`
   `artifact/REPRODUCIBILITY_STATUS.md`
   `artifact/VERIFICATION_LOG_2026-04-29.md`
   `artifact/CANONICAL_REVIEWER_PACKAGE.md`
   `artifact/SOURCE_AND_DATA.md`
   `artifact/KNOWN_LIMITATIONS.md`

The full threshold-sensitivity table for every reported prior-quality condition is in `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_audit.json`, `paper/tbl_prior_quality_response.md`, and `paper/tbl_prior_quality_response.json`.

## What The Reviewer Scripts Do

The reviewer-first scripts regenerate paper tables and figure-support files from packaged cached outputs and raw-result JSONs. They do not call an LLM and do not rebuild raw generations.

The main regeneration command currently rebuilds:

- conclusion-shift table
- statistics/cost table
- budget-sweep figure support
- bad-prior breakdown
- prior-quality response audit table, JSON, and response-curve source
- controlled degradation pilot table from packaged cached outputs
- backend replicate boundary table from stored Granite/StarCoder2 summaries and raw-result pointers

The provenance verification command checks that the prompt-only matcher constants and query-side access boundary are visible in `retrieval/prompt_structural.py`, that raw `structure_fidelity` fields are present in representative packaged raw-result files, and that the prior-quality response audit table can be regenerated from cached outputs.

The verification script is intentionally readable: it checks the exact matcher constants, asserts that the `retrieve` function does not access `query.code` or `query.tests`, checks raw-result fields, and then runs `scripts/67_make_prior_quality_audit.py`.

## What Requires Live Inference

Full experiment reruns require the packaged source and episodes plus an available model endpoint or local model matching the recorded backend configuration. These reruns are separate from paper-object regeneration.

The main backend identity is recorded as `Qwen/Qwen2.5-Coder-7B-Instruct`; supplementary backends include `deepseek-ai/deepseek-coder-6.7b-instruct`, local chat-served `ibm-granite/granite-8b-code-instruct-4k`, local completion-style `bigcode/starcoder2-7b`, and the weak StarCoder-family boundary backend. Model availability, endpoint configuration, hardware, and runtime versions affect live rerun feasibility.

## Safety Boundary

Generated Python code should be treated as untrusted code. Any live rerun that executes candidate programs should be run only in an isolated environment without sensitive credentials or network access. Resource limits reduce accidental harm but do not prove generated code is safe.

## Non-Claims

This artifact is for claim traceability. It is not a new benchmark, not a deployment-time selector, not a prompt-only structural retrieval method, and not a claim that all upstream benchmark resources can be publicly redistributed.
