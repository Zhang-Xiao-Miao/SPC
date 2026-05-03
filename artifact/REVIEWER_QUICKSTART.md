# Reviewer Quickstart

Run from the artifact root:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

## Requirements for quickstart

- GPU: not required
- API key: not required
- LLM endpoint: not required
- Network: not required
- Executes generated code: no
- Expected runtime: about 1 minute on a standard CPU environment
- Python dependencies: standard library plus packaged repository modules; see `requirements.txt`

## Expected PASS output

The exact order may vary slightly, but the scripts should end with these lines:

```text
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

No live LLM inference is required for the quickstart.

## Runtime table

| Command | Expected runtime | Requires GPU? | Calls LLM? | Executes generated code? |
| --- | ---: | --- | --- | --- |
| `bash artifact/reproduce_main.sh` | ~30 sec | no | no | no |
| `bash artifact/verify_provenance.sh` | ~20 sec | no | no | no |
| live reruns | hours/days | yes/endpoint | yes | yes |

Start with:

1. `artifact/CLAIM_TO_EVIDENCE.md`
2. `artifact/KNOWN_LIMITATIONS.md`
3. `paper/tbl_prior_quality_response.md`
4. `paper/tbl_backend_replicate_boundary.md`
5. `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`

## Troubleshooting

- If Python cannot import local modules, run from the artifact root.
- If cached outputs are missing, verify archive extraction completed.
- If live rerun scripts are invoked accidentally, stop and use the quickstart scripts only.
- If a shell reports permission issues for scripts, invoke them with `bash path/to/script.sh`.
