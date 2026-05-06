# SPC-Audit Anonymous Artifact

## What This Artifact Is

This package accompanies the NeurIPS 2026 E&D submission "Auditing Quality-Conditioned Structural-Prior Claims in Code Generation". The paper studies structural-prior evaluation as an evaluation-design problem: after matching candidate budget, accounting for execution calls, disclosing information access, separating diagnostic from deployable selection, and auditing prior quality, which structural-prior claim remains warranted?

This package is both a complete experimental codebase for the structural-prior evaluation pipeline and a reviewer-fast claim-audit/provenance package for checking the paper's evidence path. It contains code for episode construction, retrieval and prior construction, candidate generation, diagnostic execution-based selection, evaluation, table construction, cached-output regeneration, and provenance verification.

The contribution is SPC-Audit, a reviewer-inspectable reporting pattern and claim-audited artifact. It is not a deployable code-generation system, new benchmark, leaderboard submission, broad-transfer result, backend-invariance result, strongest-method claim, or deployment-safety claim.

## Start Here

Run these commands from the extracted artifact root:

```bash
cat artifact/REVIEWER_WORKFLOW.md
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

`reviewer_audit.sh` is the main reviewer-facing verifier: it prints the headline numbers, where they came from, how they were recomputed, and what claim each number does or does not support. `reproduce_main.sh` then regenerates paper-facing tables from packaged cached outputs, and `verify_provenance.sh` checks prompt-only matcher / prior-quality provenance. These three commands do not call an LLM, require a GPU, require an API key, require network access, or execute generated code.

## If You Only Have 10 Minutes

Run:

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

These commands verify the paper-facing claim-to-evidence path from cached outputs. They do not call an LLM, do not require GPU/API keys/network, and do not execute generated code.

After running them, check:

- main matched-budget result: `178.67 -> 185.00`;
- paired directionality: `30 improved` vs. `11 regressed`;
- prompt-only boundary: full MBPP+224 prompt-only rerun is non-positive;
- quality response: medium/high fidelity net `+17`, low fidelity net `+2`;
- provenance checks: prompt-only query-side access boundary and stored `structure_fidelity`.

## What Do The PASS Messages Mean?

The PASS messages mean that the artifact can regenerate and verify the derived paper-facing evidence from packaged cached outputs. They do not mean that all LLM generations were rerun. The default reviewer path checks table regeneration, prompt-only matcher constants, query-side prompt-only access boundaries, stored `structure_fidelity` fields, prior-quality audit regeneration, and claim-to-evidence consistency.

## Full Experiment Rerun At A Glance

The quickstart above verifies the paper claims from packaged raw-result JSONs. To regenerate raw model outputs and rerun the full main experiment, start with:

```bash
cat artifact/FULL_REPRODUCTION_GUIDE.md
bash artifact/check_live_rerun_prereqs.sh
```

The full live rerun requires preparing MBPP/EvalPlus-derived data under `data/`, building the episode files, starting a Qwen OpenAI-compatible endpoint at `http://127.0.0.1:8000/v1`, then running `scripts/51_run_mbpp224_fair_budget.py` with the matched-budget settings in the guide. This path calls an LLM and executes generated Python code, so it should be run in Linux/WSL/container-style isolation rather than as the default reviewer quickstart.

## Important Windows Smoke-Test Note

Python's `resource` module is Unix-only. This artifact treats it as optional: Linux/WSL/macOS use POSIX resource limits, while Windows smoke tests use `subprocess` timeout. On Windows, run:

```bash
python scripts/71_run_pipeline_smoke_test.py
```

If a stale artifact copy reports `ModuleNotFoundError: No module named 'resource'`, it is an environment-compatibility bug in that stale copy, not a paper-result failure. Use the updated package or the direct Python smoke-test entry point above.

## What The Paper Claims

- C0: the older `167/224 -> 184/224` comparison is an operational pipeline gain, but it is entangled and not attributed to the structural prior alone.
- C1: the supported positive result is a scoped fixed code-aware diagnostic effect on `MBPP+224`: `no_prior + MBR = 178.67 +/- 0.58` and `multi_prior + MBR = 185.00 +/- 1.73`.
- C2: the main scientific finding is quality-conditioned evaluation: intended code-aware priors show most positive movement in medium/high retrospective-fidelity bins, while low-quality or misleading priors can shrink or reverse gains.
- C3: full `MBPP+224` prompt-only structural retrieval is not supported: `no_prior = 179.33 +/- 2.31`, `multi_prior = 177.67 +/- 1.53`.
- C4: broad transfer, backend invariance, strongest-method performance, deployment-time `MBR-exec`, causal mechanism proof, and deployable prior-quality estimation are explicit non-claims.

The authoritative final LaTeX source edited by the expert is in `neurips2026_ed_latex_source_FINAL_v2/paper.tex`; the OpenReview paper PDF should be uploaded separately. This artifact includes the final source, checklist, figure asset, NeurIPS style file, and the paper-facing evidence objects that support the claims.

## Final Paper Object Map

| Final paper object | Artifact support |
| --- | --- |
| Figure 1: claim-audit logic | `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png` |
| Table 1: claim audit card | `artifact/CLAIM_SURVIVAL_CARD.md`, `paper/claim_matrix_v2.md` |
| Table 2: SPC-Audit checklist | `paper/audit_reporting_checklist.md`, `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md` |
| Table 3: main MBPP+224 matched-budget result | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json` |
| Table 4: prior-quality response | `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json` |
| Table 5: prompt-only boundary controls | `paper/tbl_prompt_only_structural_mbpp224_control.md` |
| Table 6: compact boundary instantiations | `paper/tbl_boundary_instantiations.md` |

The authoritative paper for review is the PDF uploaded to OpenReview. The final LaTeX source package in `neurips2026_ed_latex_source_FINAL_v2/` is provided for artifact-paper mapping; stale draft PDFs under older paths are intentionally excluded from the review zip.

## Main Evidence Map

| Reviewer question | Where to look |
| --- | --- |
| What is the final paper source? | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `checklist_filled.tex`, `figure1_claim_audit_logic.*` |
| What claims are supported or unsupported? | `artifact/CLAIM_TO_EVIDENCE.md`, `artifact/CLAIM_SURVIVAL_CARD.md`, `artifact/KNOWN_LIMITATIONS.md` |
| Can I verify the paper's exact numeric claims quickly? | `artifact/reviewer_audit.sh`, `scripts/70_reviewer_claim_audit.py` |
| Can paper-facing tables be regenerated? | `artifact/reproduce_main.sh`, `scripts/61_make_conclusion_shift_table.py`, `scripts/58_make_stats_and_cost.py`, `scripts/67_make_prior_quality_audit.py` |
| Is prompt-only matching query-prompt-only on the query side? | `artifact/verify_provenance.sh`, `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |
| Does the prior-quality audit read stored fields rather than tune retrieval? | `artifact/verify_provenance.sh`, `paper/prior_quality_audit_provenance.md`, `paper/tbl_prior_quality_response.md` |
| Where are the raw-result files for the main table? | `results/mbpp224_fair_budget/*.json`, `results/mbpp224_fair_budget/summary.json` |
| Where are prompt-only boundary outputs? | `results/prompt_only_structural_mbpp224_fair_budget/*.json`, `paper/tbl_prompt_only_structural_mbpp224_control.md` |
| Where are external/backend boundary outputs? | `paper/tbl_boundary_instantiations.md`, `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` |
| Can I run any project code end-to-end locally? | `artifact/run_smoke_test.sh`, `scripts/71_run_pipeline_smoke_test.py` |
| What requires live LLM inference and full data/model setup? | `artifact/FULL_REPRODUCTION_GUIDE.md`, `artifact/check_live_rerun_prereqs.sh`, `artifact/REPRODUCIBILITY_STATUS.md`, `artifact/SOURCE_AND_DATA.md`, `artifact/ENVIRONMENT.md` |

## Recommended Reading Order

1. `artifact/REVIEWER_QUICKSTART.md`
2. `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`
3. `artifact/OUTPUT_INTERPRETATION_GUIDE.md`
4. `artifact/CLAIM_TO_EVIDENCE.md`
5. `artifact/KNOWN_LIMITATIONS.md`
6. `artifact/LIVE_RERUN_GUIDE.md`

For deeper inspection, start with `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`.

## Code And Reproduction Modes

The artifact includes the complete executable project source tree used by the paper-facing scripts: `plan_b/`, `generation/`, `retrieval/`, `structure/`, `gating/`, `rerank/`, `guardrails/`, `eval/`, `verifier/`, `scripts/`, and `configs/`.

There are three reproduction modes:

1. Reviewer quickstart / cached-output regeneration: regenerates derived paper objects from packaged result JSONs. This is the default path for artifact review and requires only Python plus packaged repo modules.
2. Local pipeline smoke test: `bash artifact/run_smoke_test.sh` builds a one-task synthetic dataset and runs the real pipeline with the non-LLM `retrieval_edit` backend. It proves that the project code path executes, but it is not paper evidence.
3. Live experiment reruns: rebuild raw generations and execute generated code on MBPP+/HumanEval+/BigCodeBench-style inputs. This requires upstream benchmark assets, matching model endpoints or local models, optional GPU infrastructure, and an isolated execution environment. Start with `artifact/FULL_REPRODUCTION_GUIDE.md`, then run `bash artifact/check_live_rerun_prereqs.sh` to see exactly which data files, optional Python modules, and local endpoints are still missing.

Large upstream-derived benchmark data and tests are externalized from the direct review zip because the local `data/` tree is multi-GB and includes benchmark-derived assets whose redistribution requires upstream permission checks. The package instead includes cached outputs, raw-result JSONs, preparation scripts, expected layouts, provenance notes, and hashes/manifests for review.

## Canonical Evidence Objects

- Final paper source: `neurips2026_ed_latex_source_FINAL_v2/paper.tex`
- Main fair-budget table: `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json`
- Conclusion-shift table: `paper/tbl_conclusion_shift.md`, `paper/tbl_conclusion_shift.json`
- Stats/cost and paired directionality: `paper/tbl_stats_cost.md`, `paper/tbl_task_clustered_paired_stats.md`
- Prompt-only boundary controls: `paper/tbl_prompt_only_lexical_control.md`, `paper/tbl_prompt_only_structural_control.md`, `paper/tbl_prompt_only_structural_mbpp224_control.md`
- Prior-quality response: `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`
- Bad-prior harm decomposition: `paper/fig_bad_prior_delta_types.md`, `paper/bad_prior_failure_breakdown.md`
- Boundary instantiations: `paper/tbl_boundary_instantiations.md`, `paper/tbl_external_v2.md`, `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md`
- Reusable audit resources: `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md`
- Package integrity: `artifact/manifest.json`, `artifact/manifest_with_hashes.json`, `artifact/PACKAGE_AUDIT.md`; the transport zip SHA256 is provided as the sidecar file `artifact/planb_ed_artifact_anon.sha256` next to the zip, not inside the zip.

## Safety And Data Release

Generated Python code is untrusted. The reviewer quickstart does not execute generated code. Live reruns that execute generated programs should be run only in an appropriate sandbox without sensitive credentials or network access.

Public release follows `artifact/DATA_RELEASE_POLICY.md`: upstream benchmark datasets or tests are redistributed only when permission is verified. Otherwise the release should provide preparation scripts, metadata, expected directory layout, hashes, and cached-output provenance.
