# Paper To Artifact Map

## Final Paper Object Numbering

| Final paper object | Artifact support |
| --- | --- |
| Figure 1: claim-audit logic | `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.pdf` |
| Table 1: claim audit card and survival hierarchy | `artifact/CLAIM_SURVIVAL_CARD.md`, `paper/claim_matrix_v2.md` |
| Table 2: SPC-Audit reporting checklist | `paper/audit_reporting_checklist.md`, `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md` |
| Table 3: main MBPP+224 matched-budget result | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json` |
| Table 4: prior-quality response card | `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json` |
| Table 5: prompt-only boundary controls | `paper/tbl_prompt_only_structural_mbpp224_control.md`, `results/prompt_only_structural_mbpp224_fair_budget/summary.json` |
| Table 6: compact boundary instantiations | `paper/tbl_boundary_instantiations.md` |

The authoritative paper for review is the PDF uploaded to OpenReview. The final LaTeX source package here is provided for artifact-paper mapping; stale draft PDFs under older paths are intentionally excluded from the review zip.

| Paper Object | Artifact Location |
| --- | --- |
| expert-edited final paper source | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`, `neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty` |
| one-page reviewer quickstart | `artifact/REVIEWER_QUICKSTART.md` |
| reviewer workflow and explanatory audit | `artifact/REVIEWER_WORKFLOW.md`, `artifact/reviewer_audit.sh`, `scripts/70_reviewer_claim_audit.py` |
| live rerun and smoke-test guide | `artifact/LIVE_RERUN_GUIDE.md`, `artifact/FULL_REPRODUCTION_GUIDE.md`, `artifact/check_live_rerun_prereqs.sh`, `artifact/EXPERIMENT_RERUN_GUIDE.md`, `artifact/run_smoke_test.sh`, `scripts/71_run_pipeline_smoke_test.py`, `scripts/72_check_live_rerun_prereqs.py` |
| conclusion-shift table | `paper/tbl_conclusion_shift.md`, `paper/tbl_conclusion_shift.json` |
| full `MBPP+224` fair-budget table | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json` |
| stats/cost fairness table | `paper/tbl_stats_cost.md`, `paper/tbl_stats_cost.json` |
| task-clustered paired stats | `paper/tbl_task_clustered_paired_stats.md` |
| prompt-only boundary controls | `paper/tbl_prompt_only_lexical_control.md`, `paper/tbl_prompt_only_structural_control.md`, `paper/tbl_prompt_only_structural_mbpp224_control.md`, `results/prompt_only_*/*.json` |
| prompt-only structural matcher specification | `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |
| prior-quality response audit | `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_audit.json`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`, `paper/prior_quality_audit_provenance.md`, `scripts/67_make_prior_quality_audit.py`, `scripts/68_make_prior_quality_response.py` |
| claim survival hierarchy | `artifact/CLAIM_SURVIVAL_CARD.md`, `paper/claim_matrix_v2.md` |
| controlled degradation protocol and pilot | `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`, `paper/tbl_controlled_degradation_sweep.md`, `results/degradation_sweep/*.json` |
| provenance validation checklist | `paper/provenance_validation_checklist.md`, `artifact/verify_provenance.sh` |
| reusable audit checklist | `paper/audit_reporting_checklist.md` |
| data release policy | `artifact/DATA_RELEASE_POLICY.md`, `paper/data_release_policy.md` |
| reviewer-facing artifact walkthrough | `paper/artifact_reviewer_walkthrough.md` |
| contribution and artifact summary | `paper/contribution_and_artifact_summary.md` |
| final submission QA checklist | `paper/final_submission_qa_checklist.md` |
| latest verification log | `artifact/VERIFICATION_LOG.md`, `artifact/VERIFICATION_LOG_2026-05-06.md` |
| budget sweep with uncertainty | `paper/fig_budget_sweep_v2.md`, `paper/fig_budget_sweep_v2.json`, `results/budget_sweep/*.json` |
| no-rerank directionality provenance | `paper/tbl_no_rerank_directionality_v2.md`, `results/mbppplus_vllm_v4_100_oracle.json`, `results/mbppplus_vllm_v4_100_no_structure.json`, `results/mbppplus_vllm_v4_100_random.json`, `results/mbppplus_vllm_v4_100_corrupted.json` |
| external evidence table | `paper/tbl_external_v2.md`, `paper/external_protocol.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed1.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed2.md`, `paper/tbl_external_modern50_deepseek.md` |
| cross-model table | `paper/tbl_cross_model_v2.md`, `paper/tbl_cross_model_v2.json`, `paper/tbl_cross_model_deepseek_two_seed.md`, `paper/tbl_cross_model_deepseek_two_seed.json`, `paper/tbl_cross_model_starcoder2_two_seed.md`, `paper/tbl_cross_model_starcoder2_two_seed.json` |
| boundary instantiations | `paper/tbl_boundary_instantiations.md` |
| replicate-sensitive backend boundary checks | `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, `paper/backend_replicate_boundary_notes.md` |
| bad-prior harm decomposition | `paper/fig_bad_prior_delta_types.md`, `paper/fig_bad_prior_delta_types.json`, `paper/bad_prior_failure_breakdown.md` |
| concept figure support | `paper/figure1_concept.md`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.pdf` |
| final LaTeX source package | `neurips2026_ed_latex_source_FINAL_v2/README_SOURCE.md`, `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex`, `neurips2026_ed_latex_source_FINAL_v2/references.bib`, `neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty` |
| canonical backend and protocol identity | `paper/experimental_setup_v2.md`, `artifact/ENVIRONMENT.md` |
| bibliography starter and related-work notes | `paper/refs_planb.bib`, `paper/related_work_notes.md`, `paper/reference_inventory.md` |
| executable source tree | `plan_b/`, `generation/`, `retrieval/`, `structure/`, `gating/`, `rerank/`, `guardrails/`, `eval/`, `verifier/`, `scripts/`, `configs/` |
| main benchmark data and episodes | externalized from the direct review zip; see `artifact/SOURCE_AND_DATA.md`, `artifact/DATA_RELEASE_POLICY.md`, and the result-file provenance paths |
| external rerun inputs | externalized from the direct review zip; see `artifact/SOURCE_AND_DATA.md` for expected layout, redistribution status, and replacement plan |
| old uncontrolled regime provenance | `results/mbppplus_full_k1_syntax_noprior_nogate_nombr_vllm_seed1.json`, `results/mbppplus_full_k1_syntax_multiprior_nogate_mbrexec_vllm_seed1.json` |
