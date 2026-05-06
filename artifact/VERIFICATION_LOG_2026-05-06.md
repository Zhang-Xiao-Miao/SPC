# Artifact Verification Log

Date: 2026-05-06
Package: `planb_ed_artifact_anon.zip`
Archive SHA256: written after zip creation to sidecar file `artifact/planb_ed_artifact_anon.sha256`; the zip hash is not embedded inside the archive to avoid self-referential hash churn.

This log records the reviewer-script verification summary for the anonymous E&D artifact package after syncing the artifact to the expert-edited final paper source in `neurips2026_ed_latex_source_FINAL_v2/`.

## Commands

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
bash artifact/check_live_rerun_prereqs.sh
bash artifact/check_live_rerun_prereqs.sh --check-endpoints
bash artifact/run_smoke_test.sh
python -m py_compile scripts/61_make_conclusion_shift_table.py scripts/58_make_stats_and_cost.py scripts/65_make_budget_sweep_v2.py scripts/66_make_bad_prior_breakdown.py scripts/67_make_prior_quality_audit.py scripts/68_make_prior_quality_response.py scripts/69_run_controlled_degradation_sweep.py scripts/70_reviewer_claim_audit.py scripts/71_run_pipeline_smoke_test.py scripts/72_check_live_rerun_prereqs.py
python scripts/01_build_episodes.py --help
python scripts/03_prepare_evalplus.py --help
python scripts/51_run_mbpp224_fair_budget.py --help
python scripts/55_run_external_slice.py --help
python scripts/62_prepare_bigcodebench_slice.py --help
python scripts/63_run_bigcodebench_slice.py --help
python scripts/51_run_mbpp224_fair_budget.py --dataset mbppplus224 --retrieval syntax_aware --settings no_prior,multi_prior --budget 2 --seeds 1 --max-episodes 3 --generator-backend retrieval_edit --device cpu --out /tmp/planb_mbpp_live_path_sanity/summary.json --paper-out /tmp/planb_mbpp_live_path_sanity/summary.md
CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server --model <HF_CACHE>/hub/models--Qwen--Qwen2.5-Coder-7B-Instruct/snapshots/c03e6d358207e414f1eca0bb1891e29f1db0e242 --served-model-name Qwen/Qwen2.5-Coder-7B-Instruct --host 127.0.0.1 --port 8000 --gpu-memory-utilization 0.50 --max-model-len 4096 --trust-remote-code
python scripts/72_check_live_rerun_prereqs.py --check-endpoints
python scripts/51_run_mbpp224_fair_budget.py --dataset mbppplus224 --retrieval syntax_aware --settings no_prior,multi_prior --budget 1 --seeds 1 --max-episodes 2 --generator-backend vllm_openai --model-name Qwen/Qwen2.5-Coder-7B-Instruct --api-base http://127.0.0.1:8000/v1 --device cpu --out /tmp/planb_qwen_live_sanity/summary.json --paper-out /tmp/planb_qwen_live_sanity/summary.md
python scripts/59_package_ed_artifact.py
PATH=<PROJECT_ROOT>/.texlive/2026/bin/x86_64-linux:$PATH latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
```

## Results

- `reviewer_audit.sh`: PASS
- `reproduce_main.sh`: PASS with `python -S` safe runner and per-step timeout wrapper
- `verify_provenance.sh`: PASS with `python -S` safe runner for inline checks and script calls
- `check_live_rerun_prereqs.sh`: PASS as a diagnostic report; expected missing live data/modules/endpoints do not block cached-output review
- `check_live_rerun_prereqs.sh --check-endpoints` before starting a local Qwen server: diagnostic completed; default reviewer files/data/modules were present, while local model endpoints were not reachable
- temporary Qwen vLLM endpoint at `127.0.0.1:8000`: PASS; `/v1/models` returned `Qwen/Qwen2.5-Coder-7B-Instruct`
- `check_live_rerun_prereqs.sh --check-endpoints` after starting Qwen: PASS for Qwen main endpoint; DeepSeek/StarCoder2/Granite boundary endpoints remained optional-live-missing
- `run_smoke_test.sh`: PASS in the packaging environment with `python -S` and timeout wrapper
- live-rerun script interface check: PASS for `scripts/01_build_episodes.py`, `scripts/03_prepare_evalplus.py`, `scripts/51_run_mbpp224_fair_budget.py`, `scripts/55_run_external_slice.py`, `scripts/62_prepare_bigcodebench_slice.py`, and `scripts/63_run_bigcodebench_slice.py`
- MBPP+224 real-data live-path sanity check with non-LLM `retrieval_edit`: PASS for data loading, episode loading, pipeline execution, sandboxed candidate execution, and output writing; not used as paper evidence
- MBPP+224 tiny Qwen live sanity check: PASS for endpoint integration, chat-completion generation, sandboxed evaluation, and output writing on 2 episodes with `settings=no_prior,multi_prior`, `budget=1`, `seed=1`; not used as paper evidence
- Prompt-only matcher constants: PASS
- Raw `structure_fidelity` fields: PASS
- Prior-quality response regeneration: PASS
- No live LLM inference required for reviewer quickstart: PASS
- Full raw LLM regeneration: NOT RUN; only the tiny Qwen sanity check was executed, not the full multi-seed, full-task rerun or the boundary endpoint reruns

## Observed Key Outputs

```text
[PASS] reviewer claim audit matched the paper's headline numbers and boundaries
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
- The package includes the expert-edited final paper source package: `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, filled checklist, NeurIPS style file, and claim-audit figure assets.
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

- Authoritative final source: `neurips2026_ed_latex_source_FINAL_v2/paper.tex`.
- The OpenReview paper PDF should be uploaded separately from this artifact.
- In the current packaging shell, LaTeX compilation is blocked by an incomplete local TeX font/style installation. The artifact quickstart does not depend on LaTeX compilation.

## Boundary

The reviewer scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not call an LLM and do not regenerate raw model completions.
