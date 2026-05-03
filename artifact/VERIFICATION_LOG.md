# Artifact Verification Log

Date: 2026-05-03
Package: `planb_ed_artifact_anon.zip`

This log records the final reviewer-script verification summary for the anonymous E&D artifact package after the artifact-audit fixes: direct-zip size reduction, filled information-access card, generic documentation aliases, commit-hash anonymization, and reviewer-friendly PASS output.

## Commands

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
python -m py_compile scripts/61_make_conclusion_shift_table.py scripts/58_make_stats_and_cost.py scripts/65_make_budget_sweep_v2.py scripts/66_make_bad_prior_breakdown.py scripts/67_make_prior_quality_audit.py scripts/68_make_prior_quality_response.py scripts/69_run_controlled_degradation_sweep.py
python scripts/59_package_ed_artifact.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Results

- `reproduce_main.sh`: PASS
- `verify_provenance.sh`: PASS
- Prompt-only matcher constants: PASS
- Raw `structure_fidelity` fields: PASS
- Prior-quality response regeneration: PASS
- No live LLM inference required for reviewer quickstart: PASS

## Observed Key Outputs

```text
[PASS] regenerated main reviewer-facing tables and figures from cached results
[PASS] prompt_structural matcher constants verified
[PASS] query-side prompt-only access boundary verified
[PASS] raw structure_fidelity fields verified
[PASS] verified matcher provenance and regenerated prior-quality audit from cached outputs
```

## Package Checks

- `artifact/manifest_with_hashes.json` reports packaged file hashes and the package manifest reports 0 missing files.
- `artifact/manifest.json` and `artifact/manifest_with_hashes.json` omit Git commit hashes for double-blind review.
- The direct review zip excludes large upstream-derived benchmark files and is checked to remain below `100,000,000` bytes.
- The package includes `paper/latex/neurips_2026.sty`.
- The package includes `paper/contribution_and_artifact_summary.md`.
- The package includes `paper/final_submission_qa_checklist.md`.
- The package includes `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md`, `artifact/CANONICAL_REVIEWER_PACKAGE.md`, and `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`.
- The package includes generic aliases: `artifact/VERIFICATION_LOG.md`, `artifact/PACKAGE_AUDIT.md`, and `artifact/DATA_RELEASE_POLICY.md`.
- The package includes `paper/tbl_boundary_instantiations.md`.
- The package includes `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, and `paper/backend_replicate_boundary_notes.md`.
- The package includes `paper/tbl_controlled_degradation_sweep.md` and `results/degradation_sweep/*.json`.
- The package includes the prior-quality response table, JSON, and response-curve source.
- The package excludes historical worklogs, reviewer-attack notes, rebuttal drafts, and stale manuscript-planning files from the canonical anonymous archive.

## LaTeX Check

- Local draft PDF: `paper/latex/main.pdf`
- Page count: 9 pages at the time of this verification.
- The checked log had no `LaTeX Error`, `Fatal error`, or unresolved citation warnings.

## Boundary

The reviewer scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not call an LLM and do not regenerate raw model completions.
