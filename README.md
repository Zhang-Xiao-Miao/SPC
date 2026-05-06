# SPC-Audit Anonymous Artifact

This artifact accompanies the NeurIPS 2026 E&D submission:

> Auditing Quality-Conditioned Structural-Prior Claims in Code Generation

## What Is This Artifact?

This package is both:

1. a complete experimental codebase for the structural-prior evaluation pipeline; and
2. a reviewer-fast claim-audit and provenance package for checking the paper's evidence path.

It contains code for episode construction, retrieval and prior construction, candidate generation, diagnostic execution-based selection, evaluation, table construction, cached-output regeneration, and provenance verification.

It is not a deployable code-generation system, a new benchmark, a leaderboard package, a strongest-method claim, a broad-transfer claim, or a backend-invariance claim.

## What Should Reviewers Do First?

Run from the artifact root:

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

These commands do not call an LLM, do not require GPU/API/network access, and do not execute untrusted generated code.

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

The PASS messages mean that the artifact can regenerate and verify the derived paper-facing evidence from packaged cached outputs. They do not mean that all LLM generations were rerun.

The default reviewer path checks:

- paper-facing table regeneration;
- prompt-only matcher constants;
- query-side prompt-only access boundaries;
- stored `structure_fidelity` fields;
- prior-quality audit regeneration;
- claim-to-evidence consistency.

## Main Claim-To-File Map

| Paper claim | What to open | What to expect |
| --- | --- | --- |
| C0 uncontrolled gain | `paper/tbl_conclusion_shift.md` | `167/224 -> 184/224`, operational and entangled |
| C1 matched-budget effect | `paper/b_mbpp224_fair_budget.md` | `178.67 -> 185.00`, scoped code-aware diagnostic claim |
| C2 quality-conditioned claim | `paper/tbl_prior_quality_response.md` | medium/high-fidelity intended priors positive; low-fidelity coverage limits average gain |
| C3 prompt-only unsupported | `paper/tbl_prompt_only_structural_mbpp224_control.md` | full prompt-only structural rerun is non-positive |
| C4 non-claims | `paper/tbl_boundary_instantiations.md`, `artifact/KNOWN_LIMITATIONS.md` | external/backend rows are mixed, slice-sensitive, or replicate-sensitive boundary evidence |

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

## Where Is The Full Project Code?

- `configs/`: experiment configuration files.
- `plan_b/`: core pipeline, schemas, and I/O utilities.
- `generation/`: candidate generation and prompt construction utilities.
- `retrieval/`: lexical, syntax-aware, and prompt-only retrieval utilities.
- `structure/`: structure extraction and prior support utilities.
- `gating/`: prior/gating support code.
- `rerank/`: diagnostic MBR-exec selection and sandbox runner.
- `guardrails/`: guardrail helpers used by the pipeline.
- `eval/`: execution-based evaluation utilities.
- `verifier/`: static and learned verifier utilities.
- `scripts/`: experiment runners and table/audit builders.
- `results/`: cached outputs and summaries used for paper-facing regeneration.
- `paper/`: derived paper-facing tables and figure-support files.
- `artifact/`: reviewer-facing guides, scripts, claim maps, and provenance checks.

## Why Not Rerun All LLM Experiments By Default?

Full live reruns require matching model endpoints or local model weights, upstream benchmark assets, GPU/serving resources, and sandboxed execution of generated Python code. They may not reproduce bit-identical raw completions because of model-serving nondeterminism.

The reviewer quickstart therefore verifies the paper's claim-to-evidence path from packaged cached outputs. Live reruns are optional and documented in `artifact/LIVE_RERUN_GUIDE.md` and `artifact/FULL_REPRODUCTION_GUIDE.md`.

Start a live-rerun readiness check with:

```bash
bash artifact/check_live_rerun_prereqs.sh
```

Items reported as live-rerun-only are not required for the default reviewer audit path.

## Important Windows Smoke-Test Note

Python's `resource` module is Unix-only. This artifact treats it as optional: Linux/WSL/macOS use POSIX resource limits, while Windows smoke tests use `subprocess` timeout.

On Windows, run the smoke test directly from the artifact root:

```bash
python scripts/71_run_pipeline_smoke_test.py
```

If a stale artifact copy reports `ModuleNotFoundError: No module named 'resource'`, it is an environment-compatibility bug in that stale copy, not a paper-result failure. Use the updated package or the direct Python smoke-test entry point above.

## Recommended Reading Order

1. `artifact/REVIEWER_QUICKSTART.md`
2. `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`
3. `artifact/OUTPUT_INTERPRETATION_GUIDE.md`
4. `artifact/CLAIM_TO_EVIDENCE.md`
5. `artifact/KNOWN_LIMITATIONS.md`
6. `artifact/LIVE_RERUN_GUIDE.md`

For deeper inspection, start with `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`.

## Safety And Data Release

Generated Python code should be treated as untrusted. The reviewer quickstart does not execute generated code. Run live execution-based scripts only in an isolated environment with appropriate resource limits and no sensitive credentials.

Large upstream-derived benchmark data and tests are externalized from the direct review zip. Public release follows `artifact/DATA_RELEASE_POLICY.md`: upstream benchmark data or tests are redistributed only when permission is verified; otherwise the artifact provides preparation scripts, metadata, hashes, cached outputs, and expected layout.
