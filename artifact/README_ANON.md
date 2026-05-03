# Plan B Anonymous E&D Artifact

## Identity

This artifact is packaged for the NeurIPS E&D submission "Auditing Quality-Conditioned Structural-Prior Claims in Code Generation". The scientific object is evaluation design. The main contribution is SPC-Audit: a diagnostic claim-audit protocol showing that matched candidate budget, matched execution-call accounting, information access, and prior quality determine which structural-prior claim is warranted in few-shot code generation.

This artifact is not only a reproduction package. It is a claim-audit resource. Reviewers can use it to:

1. regenerate paper-facing results;
2. verify prompt-only matcher provenance;
3. verify stored `structure_fidelity` provenance;
4. inspect supported and unsupported claims;
5. reuse the audit templates for future structural-prior evaluations.

Main-result backend identity: the primary `MBPP+224` matched-budget evidence is on `Qwen/Qwen2.5-Coder-7B-Instruct`; DeepSeek is supplementary cross-model and external-support evidence; StarCoder-family runs are boundary checks.

## Canonical Paper Objects

- Table 1: conclusion-shift table (`paper/tbl_conclusion_shift.md`)
- Table 2: full `MBPP+224` fair-budget main table (`paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json`)
- Stats/cost support: `paper/tbl_stats_cost.md`
- Prompt-only boundary controls: `paper/tbl_prompt_only_lexical_control.md`, `paper/tbl_prompt_only_structural_control.md`, `paper/tbl_prompt_only_structural_mbpp224_control.md`
- Prior-quality response audit: `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`, `scripts/67_make_prior_quality_audit.py`, `scripts/68_make_prior_quality_response.py`
- Prior-quality provenance and matcher specification: `paper/prior_quality_audit_provenance.md`, `paper/prompt_only_structural_matcher.md`
- Provenance validation checklist: `paper/provenance_validation_checklist.md`, `artifact/verify_provenance.sh`
- Reusable audit checklist and data-release policy: `paper/audit_reporting_checklist.md`, `paper/data_release_policy.md`
- Claim survival hierarchy: `artifact/CLAIM_SURVIVAL_CARD.md`
- Contribution and artifact summary: `paper/contribution_and_artifact_summary.md`, `artifact/CONTRIBUTION_AND_ARTIFACT_SUMMARY.md`
- Reviewer-facing walkthrough: `paper/artifact_reviewer_walkthrough.md`
- Final submission QA checklist: `paper/final_submission_qa_checklist.md`
- Task-clustered paired stats: `paper/tbl_task_clustered_paired_stats.md`
- No-rerank directionality: `paper/tbl_no_rerank_directionality_v2.md`
- Figure 1 support: budget sweep with uncertainty (`paper/fig_budget_sweep_v2.md`, `paper/fig_budget_sweep_v2.json`)
- External evidence: `paper/tbl_external_v2.md` plus DeepSeek slice notes
- Cross-model discussion: `paper/tbl_cross_model_v2.md`, `paper/tbl_cross_model_deepseek_two_seed.md`, `paper/tbl_cross_model_starcoder2_two_seed.md`
- Boundary instantiations: `paper/tbl_boundary_instantiations.md`
- Replicate-sensitive backend boundary checks: `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md`
- Controlled degradation sweep: `paper/tbl_controlled_degradation_sweep.md`, `results/degradation_sweep/*.json`
- Concept figure support: `paper/figure1_concept.md`
- Manuscript source starter: `paper/latex/main.tex`, `paper/latex/neurips_2026.sty`

This package includes current paper-facing objects and a LaTeX starter. Historical planning drafts, reviewer-attack notes, rebuttal prewrites, response notes, and older worklogs are intentionally not part of the canonical anonymous artifact to avoid stale claim wording.

The canonical claim set is defined by `artifact/CLAIM_TO_EVIDENCE.md` and the main paper. Exploratory materials, if present, are not used as main-claim evidence unless explicitly listed in `artifact/CLAIM_TO_EVIDENCE.md`.

## Reviewer-First Reproduction

Quickstart:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

Additional focused commands are `bash artifact/reproduce_table1.sh`, `bash artifact/reproduce_figure1.sh`, and `bash artifact/reproduce_figures.sh`.

These commands regenerate paper-facing tables and figure-support files from packaged cached outputs and raw-result JSONs. They do not call an LLM, do not require a GPU, do not require network access, and do not execute generated code. Full experiment reruns require prepared upstream benchmark assets plus an available model endpoint or local model matching the recorded backend configuration.

## Navigation Aids

- `artifact/CANONICAL_FILE_LIST.md`: frozen paper-object list; use this first when writing
- `artifact/CONTRIBUTION_AND_ARTIFACT_SUMMARY.md`: compact contribution and reviewer-entry summary
- `artifact/REVIEWER_QUICKSTART.md`: one-page quickstart for reviewers
- `artifact/CLAIM_TO_EVIDENCE.md`: which files support each headline claim
- `artifact/PAPER_TO_ARTIFACT_MAP.md`: where each paper object lives on disk
- `artifact/ENVIRONMENT.md`: recovered software / serving / hardware notes
- `artifact/SOURCE_AND_DATA.md`: included code tree, externalized benchmark-data inventory, and redistribution status
- `artifact/DATA_RELEASE_POLICY.md`: public-release and review-package data policy
- `artifact/REPRODUCIBILITY_STATUS.md`: what is fully regenerable versus provenance-only
- `paper/tbl_backend_replicate_boundary.md`: Granite and StarCoder2 replicate-sensitive backend boundary table
- `paper/backend_replicate_boundary_notes.md`: raw-result pointers, serving-mode caveats, and filter-attempt transparency for backend boundary checks
- `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`: reusable audit-reporting template
- `artifact/INFORMATION_ACCESS_CARD.md`: reusable information-access disclosure card
- `artifact/CLAIM_SURVIVAL_CARD.md`: reusable claim-survival hierarchy card
- `artifact/CANONICAL_REVIEWER_PACKAGE.md`: reviewer package inventory and exclusions
- `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`: pre-registered prior-quality degradation protocol and completed DeepSeek pilot scope
- `artifact/VERIFICATION_LOG_2026-04-29.md`: latest reviewer-script verification summary
- `artifact/RESULT_NAMING_RULES.md`: backend-safe naming policy
- `artifact/KNOWN_LIMITATIONS.md`: exact scope limits and non-claims
- `artifact/manifest_with_hashes.json`: file-level hashes for packaged contents

## Safety And Data Release

Generated Python code should be treated as untrusted and run only in an appropriate sandbox with resource limits. The direct review zip externalizes large upstream-derived benchmark assets and keeps cached outputs, scripts, metadata, and hashes for inspection. The public release follows `artifact/DATA_RELEASE_POLICY.md`; upstream benchmark data or tests are redistributed publicly only when permission is verified, otherwise provenance and preparation metadata are provided.

Packaging note: the uploaded archive filename is `artifact/planb_ed_artifact_anon.zip`. That filename is a transport wrapper for the package and is not expected to appear as an internal file inside the archive.
