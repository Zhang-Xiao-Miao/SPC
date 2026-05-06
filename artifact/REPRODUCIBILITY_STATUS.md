# Reproducibility Status

## Fully Regenerable From Packaged Inputs

- Expert-edited final manuscript source is packaged at `neurips2026_ed_latex_source_FINAL_v2/paper.tex`; the OpenReview PDF should be uploaded separately from this artifact.
- `bash artifact/reviewer_audit.sh` recomputes and verifies headline claim numbers from packaged raw-result JSONs.
- `paper/tbl_conclusion_shift.md` and `paper/tbl_conclusion_shift.json`
- `paper/tbl_stats_cost.md` and `paper/tbl_stats_cost.json`
- `paper/fig_budget_sweep_v2.md` and `paper/fig_budget_sweep_v2.json`
- `paper/fig_bad_prior_delta_types.md` and `paper/fig_bad_prior_delta_types.json`
- `paper/tbl_prior_quality_audit.md` and `paper/tbl_prior_quality_audit.json`
- `paper/tbl_prior_quality_response.md` and `paper/tbl_prior_quality_response.json`
- `paper/fig_prior_quality_response.md`
- `paper/tbl_backend_replicate_boundary.md` from stored Granite/StarCoder2 boundary summaries and raw-result pointers
- `paper/tbl_controlled_degradation_sweep.md` from packaged degradation-sweep raw results

These objects can be regenerated from packaged result files and packaged scripts. This regeneration path uses cached outputs and raw-result JSONs; it does not call an LLM.

## Provenance Validation

- `bash artifact/verify_provenance.sh` checks the prompt-only matcher constants and query-side access boundary in `retrieval/prompt_structural.py`.
- The same command checks representative raw result files for stored `structure_fidelity` fields and regenerates the prior-quality audit table from cached outputs.
- `paper/provenance_validation_checklist.md` gives the corresponding manual inspection path.

## Live LLM Reruns

- `bash artifact/run_smoke_test.sh` is a local code-path smoke test using a synthetic one-task fixture and the non-LLM `retrieval_edit` backend. It is not paper evidence.
- The primary live-rerun guide is `artifact/FULL_REPRODUCTION_GUIDE.md`; `bash artifact/check_live_rerun_prereqs.sh` reports the required review files, live data files, optional Python modules, and optional `/v1/models` endpoints.
- Full experiment reruns require the packaged source and episodes plus an available model endpoint or local model matching the recorded backend configuration.
- The main backend identity is `Qwen/Qwen2.5-Coder-7B-Instruct`; supplementary reruns may require `deepseek-ai/deepseek-coder-6.7b-instruct`, local `bigcode/starcoder2-7b`, or the weak StarCoder-family boundary backend.
- Live reruns that execute generated Python code should be run only in an isolated environment without sensitive credentials or network access.
- The controlled prior-quality degradation sweep has a completed DeepSeek `MBPP+50` pilot in `paper/tbl_controlled_degradation_sweep.md` and `results/degradation_sweep/*.json`. It is secondary diagnostic evidence, not a main result.
- Granite and StarCoder2 backend-boundary checks are packaged in `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, `paper/backend_replicate_boundary_notes.md`, and the referenced raw-result JSONs. They support replicate-sensitive backend audit reporting, not backend invariance.

## Packaged Direct-Provenance Evidence

- `paper/tbl_conclusion_shift.*` includes the packaged old uncontrolled raw results it cites.
- No-rerank directionality provenance is packaged directly through:
  - `results/mbppplus_vllm_v4_100_oracle.json`
  - `results/mbppplus_vllm_v4_100_no_structure.json`
  - `results/mbppplus_vllm_v4_100_random.json`
  - `results/mbppplus_vllm_v4_100_corrupted.json`
- Prompt-only boundary controls are packaged through:
  - `paper/tbl_prompt_only_lexical_control.md`
  - `paper/tbl_prompt_only_structural_control.md`
  - `paper/tbl_prompt_only_structural_mbpp224_control.md`
  - `results/prompt_only_lexical_mbpp100_fair_budget/*.json`
  - `results/prompt_only_structural_mbpp100_fair_budget/*.json`
  - `results/prompt_only_structural_mbpp224_fair_budget/*.json`
- Replicate-sensitive backend boundary checks are packaged through:
  - `paper/tbl_backend_replicate_boundary.md`
  - `paper/tbl_backend_replicate_boundary.json`
  - `paper/backend_replicate_boundary_notes.md`
  - `results/vllm_granite8b_mbppplus100_syntax_aware_*_seed*.json`
  - `results/vllm_starcoder2_mbppplus100_syntax_aware_*_rerun_seed*.json`

## Rerunnable Main Benchmark With Live Inference

- `MBPP+224` matched-budget main benchmark is rerunnable from packaged source after reconstructing the expected benchmark data/episode layout from upstream sources. The matching model endpoint or local model is also required. Packaged raw results are provided for paper-object regeneration and inspection.

## Rerunnable External Evaluation With Live Inference

- `HumanEval+164` and `HumanEval+50` are rerunnable after reconstructing the expected benchmark data/episode layout if the matching model endpoint or local model is available.
- `BigCodeBench-Hard compatible30/50` are rerunnable after reconstructing the processed compatibility slices and packaged-episode layout under the same live-inference assumption.
- The DeepSeek `MBPP+50` degradation pilot is rerunnable after reconstructing the expected MBPP+ slice inputs if the same `deepseek-ai/deepseek-coder-6.7b-instruct` endpoint is available.

## Provenance-Only Or Partially Regenerable Steps

- The compatibility filtering step for `BigCodeBench-Hard` slice creation depends on access to a local dataset cache or equivalent upstream data export.
- The artifact includes `scripts/62_prepare_bigcodebench_slice.py` as provenance, but the direct review zip externalizes the processed slice data; live reruns require reconstructing those inputs from upstream sources.
- The package includes current paper-facing objects and the expert-edited final LaTeX source package. Reviewer quickstart does not depend on local LaTeX compilation; compiling the source requires a complete TeX installation with the NeurIPS style dependencies and fonts.
- Historical planning drafts, reviewer-attack notes, rebuttal prewrites, and older worklogs are intentionally excluded from the canonical anonymous artifact to avoid stale claim wording.

## Cached-Output Boundaries

- The reviewer-first scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not regenerate raw LLM completions.
- Some supporting historical repo objects outside the canonical file list remain archival only and should not be cited as current paper evidence.
- The uploaded archive name `artifact/planb_ed_artifact_anon.zip` is an outer transport filename, not an internal artifact path that should appear inside the package.
