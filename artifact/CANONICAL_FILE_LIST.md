# Canonical File List

Use only the following paper-facing objects when writing the manuscript or citing artifact evidence.

## Canonical Paper Objects

- `README.md`
- `requirements.txt`
- `requirements-review.txt`
- `requirements-live.txt`
- `LICENSE_REVIEW_ONLY.md`
- `paper/title.md`
- `paper/abstract_v2.md`
- `paper/intro_v2.md`
- `paper/claim_matrix_v2.md`
- `paper/experimental_setup_v2.md`
- `paper/audit_reporting_checklist.md`
- `paper/prompt_only_structural_matcher.md`
- `paper/prior_quality_audit_provenance.md`
- `paper/provenance_validation_checklist.md`
- `paper/data_release_policy.md`
- `paper/artifact_reviewer_walkthrough.md`
- `paper/contribution_and_artifact_summary.md`
- `paper/final_submission_qa_checklist.md`
- `paper/figure1_concept.md`
- `paper/external_protocol.md`
- `paper/discussion_backend_sensitivity.md`
- `paper/related_work_notes.md`
- `paper/reference_inventory.md`
- `paper/refs_planb.bib`
- `paper/b_mbpp224_fair_budget.md`
- `paper/tbl_conclusion_shift.md`
- `paper/tbl_conclusion_shift.json`
- `paper/tbl_stats_cost.md`
- `paper/tbl_stats_cost.json`
- `paper/tbl_task_clustered_paired_stats.md`
- `paper/tbl_no_rerank_directionality_v2.md`
- `paper/tbl_prompt_only_lexical_control.md`
- `paper/tbl_prompt_only_structural_control.md`
- `paper/tbl_prompt_only_structural_mbpp224_control.md`
- `paper/tbl_prior_quality_audit.md`
- `paper/tbl_prior_quality_audit.json`
- `paper/tbl_prior_quality_response.md`
- `paper/tbl_prior_quality_response.json`
- `paper/fig_prior_quality_response.md`
- `paper/fig_budget_sweep_v2.md`
- `paper/fig_budget_sweep_v2.json`
- `paper/tbl_external_v2.md`
- `paper/tbl_boundary_instantiations.md`
- `paper/tbl_backend_replicate_boundary.md`
- `paper/tbl_backend_replicate_boundary.json`
- `paper/backend_replicate_boundary_notes.md`
- `paper/b_external_slice_humanevalplus50_deepseek_seed1.md`
- `paper/b_external_slice_humanevalplus50_deepseek_seed2.md`
- `paper/tbl_external_modern30_deepseek.md`
- `paper/tbl_external_modern50_deepseek.md`
- `paper/tbl_external_modern_sampling30.md`
- `paper/tbl_external_modern_sampling50.md`
- `paper/tbl_cross_model_v2.md`
- `paper/tbl_cross_model_v2.json`
- `paper/tbl_cross_model_deepseek_two_seed.md`
- `paper/tbl_cross_model_deepseek_two_seed.json`
- `paper/tbl_cross_model_starcoder2_seed1.md`
- `paper/tbl_cross_model_starcoder2_seed2.md`
- `paper/tbl_cross_model_starcoder2_two_seed.md`
- `paper/tbl_cross_model_starcoder2_two_seed.json`
- `paper/tbl_cross_model_safe_gpu_seed2.md`
- `paper/tbl_controlled_degradation_sweep.md`
- `paper/fig_bad_prior_delta_types.md`
- `paper/fig_bad_prior_delta_types.json`
- `paper/bad_prior_failure_breakdown.md`
- `neurips2026_ed_latex_source_FINAL_v2/README_SOURCE.md`
- `neurips2026_ed_latex_source_FINAL_v2/paper.tex`
- `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex`
- `neurips2026_ed_latex_source_FINAL_v2/references.bib`
- `neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty`
- `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`
- `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.pdf`

## Canonical Families

- `results/budget_sweep/*.json`
- `results/prompt_only_*/*.json`
- `results/degradation_sweep/*.json`

The authoritative final manuscript source is `neurips2026_ed_latex_source_FINAL_v2/paper.tex`. Older repo-local `paper/latex/` draft files are not part of the canonical reviewer package.

Large upstream-derived benchmark data and tests are externalized from the direct review zip. See `artifact/SOURCE_AND_DATA.md` and `artifact/DATA_RELEASE_POLICY.md` for expected layout, hashes/provenance, and redistribution status.

## Superseded But Non-Canonical Repo Objects

- `paper/tbl_external.md`
- `paper/tbl_cross_model.md`
- `paper/fig_budget_sweep.md`
- `paper/tbl_external_modern.md`
- `paper/tbl_external_modern_sampling.md`

Those superseded files remain in the repository for historical traceability only. Do not cite them in the final manuscript or artifact map.
