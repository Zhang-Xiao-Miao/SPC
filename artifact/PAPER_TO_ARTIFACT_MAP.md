# Paper To Artifact Map

| Paper Object | Artifact Location |
| --- | --- |
| one-page reviewer quickstart | `artifact/REVIEWER_QUICKSTART.md` |
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
| latest verification log | `artifact/VERIFICATION_LOG.md`, `artifact/VERIFICATION_LOG_2026-04-29.md` |
| budget sweep with uncertainty | `paper/fig_budget_sweep_v2.md`, `paper/fig_budget_sweep_v2.json`, `results/budget_sweep/*.json` |
| no-rerank directionality provenance | `paper/tbl_no_rerank_directionality_v2.md`, `results/mbppplus_vllm_v4_100_oracle.json`, `results/mbppplus_vllm_v4_100_no_structure.json`, `results/mbppplus_vllm_v4_100_random.json`, `results/mbppplus_vllm_v4_100_corrupted.json` |
| external evidence table | `paper/tbl_external_v2.md`, `paper/external_protocol.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed1.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed2.md`, `paper/tbl_external_modern50_deepseek.md` |
| cross-model table | `paper/tbl_cross_model_v2.md`, `paper/tbl_cross_model_v2.json`, `paper/tbl_cross_model_deepseek_two_seed.md`, `paper/tbl_cross_model_deepseek_two_seed.json`, `paper/tbl_cross_model_starcoder2_two_seed.md`, `paper/tbl_cross_model_starcoder2_two_seed.json` |
| boundary instantiations | `paper/tbl_boundary_instantiations.md` |
| replicate-sensitive backend boundary checks | `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, `paper/backend_replicate_boundary_notes.md` |
| bad-prior harm decomposition | `paper/fig_bad_prior_delta_types.md`, `paper/fig_bad_prior_delta_types.json`, `paper/bad_prior_failure_breakdown.md` |
| concept figure support | `paper/figure1_concept.md` |
| manuscript source starter | `paper/latex/main.tex`, `paper/latex/neurips_2026.sty`, `paper/latex/sections/*.tex` |
| canonical backend and protocol identity | `paper/experimental_setup_v2.md`, `artifact/ENVIRONMENT.md` |
| bibliography starter and related-work notes | `paper/refs_planb.bib`, `paper/related_work_notes.md`, `paper/reference_inventory.md` |
| executable source tree | `plan_b/`, `generation/`, `retrieval/`, `structure/`, `gating/`, `rerank/`, `guardrails/`, `eval/`, `verifier/`, `scripts/`, `configs/` |
| main benchmark data and episodes | externalized from the direct review zip; see `artifact/SOURCE_AND_DATA.md`, `artifact/DATA_RELEASE_POLICY.md`, and the result-file provenance paths |
| external rerun inputs | externalized from the direct review zip; see `artifact/SOURCE_AND_DATA.md` for expected layout, redistribution status, and replacement plan |
| old uncontrolled regime provenance | `results/mbppplus_full_k1_syntax_noprior_nogate_nombr_vllm_seed1.json`, `results/mbppplus_full_k1_syntax_multiprior_nogate_mbrexec_vllm_seed1.json` |
