# Canonical Reviewer Package

This file describes the intended anonymous reviewer package. It is a navigation aid for artifact reviewers and a guardrail against stale-file contamination.

## Reviewer Quickstart

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

## First Files To Inspect

- `artifact/REVIEWER_WORKFLOW.md`
- `artifact/REVIEWER_QUICKSTART.md`
- `artifact/README_ANON.md`
- `neurips2026_ed_latex_source_FINAL_v2/paper.tex`
- `artifact/CLAIM_TO_EVIDENCE.md`
- `artifact/PAPER_TO_ARTIFACT_MAP.md`
- `artifact/KNOWN_LIMITATIONS.md`
- `artifact/REPRODUCIBILITY_STATUS.md`
- `artifact/VERIFICATION_LOG_2026-05-06.md`
- `paper/contribution_and_artifact_summary.md`
- `paper/artifact_reviewer_walkthrough.md`

## Reusable Reporting Resources

- `paper/audit_reporting_checklist.md`
- `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`
- `artifact/INFORMATION_ACCESS_CARD.md`
- `artifact/CLAIM_SURVIVAL_CARD.md`
- `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`

## Canonical Evidence Objects

- `neurips2026_ed_latex_source_FINAL_v2/paper.tex`
- `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex`
- `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`
- `paper/tbl_conclusion_shift.md`
- `paper/b_mbpp224_fair_budget.md`
- `paper/tbl_prompt_only_structural_mbpp224_control.md`
- `paper/tbl_prior_quality_response.md`
- `paper/tbl_prior_quality_audit.md`
- `paper/tbl_boundary_instantiations.md`
- `paper/tbl_backend_replicate_boundary.md`
- `paper/backend_replicate_boundary_notes.md`
- `paper/tbl_controlled_degradation_sweep.md`
- `artifact/CLAIM_SURVIVAL_CARD.md`
- `retrieval/prompt_structural.py`
- `scripts/70_reviewer_claim_audit.py`
- `scripts/71_run_pipeline_smoke_test.py`
- `scripts/67_make_prior_quality_audit.py`
- `scripts/68_make_prior_quality_response.py`
- `scripts/69_run_controlled_degradation_sweep.py`
- `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`

## Excluded From The Reviewer Package

- Historical worklogs.
- Reviewer-attack notes.
- Rebuttal drafts.
- Old paper drafts and staging notes.
- `paperB/` staging files.
- Internal strengthening plans and response notes.
- Files with stale method-paper framing.

The anonymous package is intentionally narrower than the working repository.
