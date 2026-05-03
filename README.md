# SPC-Audit Anonymous Artifact

This artifact accompanies the NeurIPS 2026 E&D submission
"Auditing Quality-Conditioned Structural-Prior Claims in Code Generation".

The artifact supports SPC-Audit: a diagnostic reporting pattern for structural-prior
claims in execution-evaluated code generation. It is not a deployable
code-generation system, a new benchmark, a leaderboard package, or a strongest-method
claim.

## Quickstart

Run from the artifact root:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

The first two commands regenerate paper-facing tables from cached outputs and verify
prompt-only matcher / prior-quality provenance. They do not call an LLM, do not
require a GPU/API key/network, and do not execute generated code.

## Main Navigation

- `artifact/README_ANON.md`: full reviewer guide
- `artifact/REVIEWER_QUICKSTART.md`: one-page reviewer entry point
- `artifact/CONTRIBUTION_AND_ARTIFACT_SUMMARY.md`: contribution and artifact contract
- `artifact/CLAIM_TO_EVIDENCE.md`: supported, qualified, and unsupported claims
- `artifact/KNOWN_LIMITATIONS.md`: exact limitations and non-claims
- `artifact/PAPER_TO_ARTIFACT_MAP.md`: table and claim provenance map
- `paper/tbl_prior_quality_response.md`: prior-quality response audit
- `paper/tbl_backend_replicate_boundary.md`: Granite / StarCoder2 boundary checks

## Cached Regeneration

Reviewer quickstart commands regenerate derived paper objects from packaged cached
outputs and raw-result JSONs. Full LLM reruns are optional and require prepared
benchmark assets plus model endpoints or local models matching the recorded
configurations.

## Safety

Generated Python code should be treated as untrusted. Run execution-based scripts
only in an isolated environment with appropriate resource limits.

## Data Release

The public release follows `artifact/DATA_RELEASE_POLICY.md` and
`paper/data_release_policy.md`. Upstream benchmark data or tests are redistributed
publicly only when permission is verified; otherwise the artifact provides
provenance, preparation scripts, metadata, hashes, and expected layout.
