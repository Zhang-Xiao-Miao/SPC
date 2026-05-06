# Project Guide for Reviewers

## Purpose

This artifact is a complete experimental codebase plus a reviewer-fast provenance package for the paper. The codebase implements the evaluation pipeline used to construct episodes, generate candidates, retrieve priors, apply diagnostic `MBR-exec` selection, evaluate generated programs, and regenerate paper-facing tables.

## Pipeline Overview

1. Episode construction creates query/support/test records.
2. Retrieval constructs code-aware and prompt-only conditions.
3. Prior construction produces single, multi, random, or corrupted priors.
4. Candidate generation produces candidate programs.
5. Diagnostic `MBR-exec` selects candidates using packaged tests.
6. Evaluation records pass/fail outcomes.
7. Table builders regenerate paper-facing summaries from cached outputs.
8. Provenance checks verify information-access and prior-quality boundaries.

## Full Codebase Directory Map

| Directory | Reviewer meaning |
| --- | --- |
| `configs/` | experiment configuration files |
| `plan_b/` | core pipeline, schemas, and I/O utilities |
| `generation/` | candidate generation and prompt construction utilities |
| `retrieval/` | lexical, syntax-aware, and prompt-only retrieval utilities |
| `structure/` | structure extraction and prior support utilities |
| `gating/` | prior/gating support code |
| `rerank/` | diagnostic `MBR-exec` selection and sandbox runner |
| `guardrails/` | guardrail helpers used by the pipeline |
| `eval/` | execution-based evaluation utilities |
| `verifier/` | static and learned verifier utilities |
| `scripts/` | experiment runners and table/audit builders |
| `results/` | cached outputs and summaries used for paper-facing regeneration |
| `paper/` | derived paper-facing tables and figure-support files |
| `artifact/` | reviewer-facing guides, scripts, claim maps, and provenance checks |

## What Is Canonical Evidence?

The canonical evidence for the paper is listed in `artifact/CLAIM_TO_EVIDENCE.md` and summarized in `artifact/PAPER_TO_ARTIFACT_MAP.md`. Exploratory files should not be used as main-claim evidence unless they are explicitly listed there.

## Reviewer-Fast Path

Use:

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

This path checks the paper-facing evidence from cached outputs. It does not call an LLM, require GPU/API/network access, or execute untrusted generated code.

## Optional Live Path

Live reruns are documented in `artifact/LIVE_RERUN_GUIDE.md` and `artifact/FULL_REPRODUCTION_GUIDE.md`. They require external assets, model endpoints, and sandboxed execution, and are not needed for the default reviewer audit.
