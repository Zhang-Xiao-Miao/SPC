# Output Interpretation Guide

## What Does `reviewer_audit.sh` Show?

It prints the paper's main claim-to-evidence chain in human-readable form:

- uncontrolled operational gain;
- matched-budget diagnostic result;
- paired directionality;
- prompt-only boundary;
- prior-quality response;
- bad-prior and boundary non-claims.

The script recomputes the reported values from packaged JSON files before printing the final PASS line.

## What Does `reproduce_main.sh` Prove?

It regenerates derived paper-facing tables from cached outputs. It proves that the reported paper tables are reconstructible from the packaged cached results. It does not rerun LLM generation.

## What Does `verify_provenance.sh` Prove?

It verifies prompt-only matcher constants, query-side access boundaries, stored `structure_fidelity` fields, and prior-quality audit regeneration.

## What Do PASS Messages Not Mean?

They do not mean:

- full live LLM reruns were performed;
- the system is deployable;
- `MBR-exec` is a deployment-time reranker;
- `structure_fidelity` is a deployable estimator;
- broad transfer or backend invariance is supported;
- all model-serving nondeterminism has been eliminated.

## How To Read The Main Numbers

| Reviewer-visible output | Paper interpretation |
| --- | --- |
| `178.67 -> 185.00` | scoped matched-budget code-aware diagnostic effect on `MBPP+224` |
| `30 improved / 11 regressed / 631 unchanged` | positive paired directionality, not a robustness claim |
| prompt-only `179.33` vs `177.67` | full prompt-only structural rerun is non-positive |
| medium/high net `+17` vs low net `+2` | prior quality conditions the observed effect |
| random/corrupted priors below baseline | misleading priors can harm under the same diagnostic selector |
