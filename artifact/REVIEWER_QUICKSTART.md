# Reviewer Quickstart

Run from the artifact root:

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

## Requirements for quickstart

- GPU: not required
- API key: not required
- LLM endpoint: not required
- Network: not required
- Executes generated code: no
- Expected runtime: about 1 minute on a standard CPU environment
- Python dependencies: standard library plus packaged repository modules; see `requirements-review.txt`

## Important Windows Smoke-Test Note

Python's `resource` module is Unix-only. The current artifact makes it optional in `rerank/sandbox_runner.py`: Linux/WSL/macOS use POSIX resource limits, while Windows smoke tests use subprocess timeout.

On Windows without `bash`, run:

```bash
python scripts/71_run_pipeline_smoke_test.py
```

If you see `ModuleNotFoundError: No module named 'resource'`, you are using a stale artifact copy. That error is an environment-compatibility issue in the stale copy, not evidence that the paper results cannot be audited.

## What each command answers

| Command | Reviewer question answered |
| --- | --- |
| `bash artifact/reviewer_audit.sh` | Do the raw packaged JSONs actually contain the headline paper numbers, paired directionality, prompt-only boundary, and prior-quality response? |
| `bash artifact/reproduce_main.sh` | Can the paper-facing tables be regenerated from cached outputs rather than hand-written? |
| `bash artifact/verify_provenance.sh` | Is the prompt-only matcher fixed/query-prompt-only, and does the prior-quality audit read stored fields? |
| `bash artifact/run_smoke_test.sh` | Optional: does the real pipeline code execute end-to-end on a local toy fixture? This runs generated toy code and is not part of the default no-execution quickstart. |

## Expected output

The audit script prints the actual numbers before the final PASS line. You should see lines like:

```text
[PASS] reviewer claim audit matched the paper's headline numbers and boundaries
[PASS] regenerated conclusion-shift table
[PASS] regenerated stats/cost table
[PASS] regenerated budget sweep support
[PASS] regenerated bad-prior breakdown
[PASS] regenerated prior-quality audit
[PASS] regenerated controlled-degradation table from cached outputs
[PASS] regenerated main reviewer-facing tables and figures from cached results
[PASS] prompt_structural matcher constants verified
[PASS] query-side prompt-only access boundary verified
[PASS] raw structure_fidelity fields verified
[PASS] prior-quality response regenerated from cached outputs
[PASS] verified matcher provenance and regenerated prior-quality audit from cached outputs
```

No live LLM inference is required for the default quickstart.

## Runtime table

| Command | Expected runtime | Requires GPU? | Calls LLM? | Executes generated code? |
| --- | ---: | --- | --- | --- |
| `bash artifact/reviewer_audit.sh` | ~10 sec | no | no | no |
| `bash artifact/reproduce_main.sh` | ~30 sec | no | no | no |
| `bash artifact/verify_provenance.sh` | ~20 sec | no | no | no |
| `bash artifact/run_smoke_test.sh` | ~10 sec | no | no | yes, toy fixture only |
| live reruns | hours/days | yes/endpoint | yes | yes |

Start with:

1. `artifact/REVIEWER_WORKFLOW.md`
2. `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`
3. `artifact/OUTPUT_INTERPRETATION_GUIDE.md`
4. `artifact/README_ANON.md`
5. `artifact/CLAIM_TO_EVIDENCE.md`
6. `artifact/KNOWN_LIMITATIONS.md`
7. `artifact/LIVE_RERUN_GUIDE.md`

## Troubleshooting

- If Python cannot import local modules, run from the artifact root.
- If cached outputs are missing, verify archive extraction completed.
- If live rerun scripts are invoked accidentally, stop and use the three default quickstart scripts only.
- If a shell reports permission issues for scripts, invoke them with `bash path/to/script.sh`.
- On Windows without `bash`, run the smoke test directly with `python scripts/71_run_pipeline_smoke_test.py` from the artifact root.
