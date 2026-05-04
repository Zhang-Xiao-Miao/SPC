# SPC-Audit Anonymous Artifact

This is the reviewer-facing artifact for the NeurIPS 2026 E&D submission
**"Auditing Quality-Conditioned Structural-Prior Claims in Code Generation."**

## What is this artifact?

This artifact is **not** a deployable code-generation system, a new benchmark, or a
leaderboard package. It is a **claim-audit and provenance package** for the paper.

The paper studies a structural-prior code-generation pipeline and asks a narrow
E&D question:

> After controlling candidate budget, execution-call accounting, information
> access, and diagnostic selection, which structural-prior claims remain
> supported?

The artifact lets reviewers verify the paper's claim-to-evidence path from
packaged cached outputs:

1. an uncontrolled operational gain is entangled;
2. the matched-budget comparison supports only a scoped code-aware diagnostic
   effect;
3. prompt-only structural retrieval is a boundary result, not a deployment claim;
4. the prior-quality audit shows why prior presence alone is insufficient;
5. bad-prior, external-slice, and backend rows define non-claims.

## If you only have 5 minutes

Run from the repository root:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

These commands are intended to be fast reviewer checks. They:

- regenerate paper-facing tables from cached result files;
- verify the prompt-only matcher constants;
- verify that prompt-only query-side matching does not use solution code;
- verify that stored `structure_fidelity` fields exist;
- regenerate the prior-quality response audit from cached outputs.

They do **not** call an LLM, do **not** require a GPU, do **not** require network
access, and do **not** execute generated code.

Expected successful output ends with PASS lines such as:

```text
[PASS] regenerated main reviewer-facing tables and figures from cached results
[PASS] prompt_structural matcher constants verified
[PASS] query-side prompt-only access boundary verified
[PASS] raw structure_fidelity fields verified
[PASS] prior-quality response regenerated from cached outputs
```

## What do the PASS outputs mean?

The PASS outputs mean that the artifact can regenerate and verify the **derived
paper-facing evidence** from packaged cached outputs. They do not mean that the
artifact reran all LLM generations.

| Command | What it checks | What it does not do |
| --- | --- | --- |
| `artifact/reproduce_main.sh` | Recreates paper-facing tables/figure-support files from cached results | Does not call an LLM; does not run live generation |
| `artifact/verify_provenance.sh` | Checks matcher constants, prompt-only access boundaries, stored fidelity fields, and prior-quality audit regeneration | Does not prove deployability; does not execute generated code |

## Main paper claims and where to inspect them

| Paper claim | What to open | What to expect |
| --- | --- | --- |
| C0: uncontrolled gain is entangled | `paper/tbl_conclusion_shift.md` | `167/224 -> 184/224`, labeled operational/entangled |
| C1: matched-budget code-aware diagnostic effect | `paper/b_mbpp224_fair_budget.md` | `no_prior + MBR = 178.67`, `multi_prior + MBR = 185.00` |
| C2: quality-conditioned evaluation claim | `paper/tbl_prior_quality_response.md` | intended priors are most positive in medium/high retrospective-fidelity bins |
| C3: prompt-only structural retrieval is unsupported | `paper/tbl_prompt_only_structural_mbpp224_control.md` | full `MBPP+224` prompt-only rerun is non-positive |
| C4: broad transfer/backend invariance are non-claims | `paper/tbl_boundary_instantiations.md` | external/backend rows are mixed or boundary-only |

For the complete map, read:

```text
artifact/CLAIM_TO_EVIDENCE.md
artifact/CLAIM_SURVIVAL_CARD.md
artifact/PAPER_TO_ARTIFACT_MAP.md
```

## How to read the artifact

Recommended order:

1. `artifact/CLAIM_TO_EVIDENCE.md` — which file supports each paper claim.
2. `artifact/KNOWN_LIMITATIONS.md` — what the paper explicitly does not claim.
3. `artifact/INFORMATION_ACCESS_CARD.md` — which components are code-aware,
   prompt-only, retrospective, or same-test diagnostic.
4. `paper/b_mbpp224_fair_budget.md` — the main matched-budget result.
5. `paper/tbl_prior_quality_response.md` — the prior-quality response audit.
6. `paper/tbl_prompt_only_structural_mbpp224_control.md` — the prompt-only
   boundary result.

## What this artifact does not claim

This artifact does **not** claim:

- a deployable structural-prior retrieval method;
- full compute equality, equal latency, or equal prompt-token usage;
- broad transfer across benchmarks;
- backend invariance;
- a new strongest code-generation method;
- a deployable prior-quality estimator;
- a causal mechanism proof;
- safety or deployment readiness.

## Cached regeneration vs. live reruns

The reviewer quickstart uses cached outputs. This is the intended fast path for
review.

Full live reruns are optional and require matching model endpoints or local
models. They may execute generated Python code, which should be treated as
untrusted and run only in a sandbox with resource limits. See:

```text
artifact/REPRODUCIBILITY_STATUS.md
artifact/ENVIRONMENT.md
artifact/SOURCE_AND_DATA.md
artifact/DATA_RELEASE_POLICY.md
```

## Navigation

- `artifact/REVIEWER_QUICKSTART.md`: one-page command guide.
- `artifact/CLAIM_TO_EVIDENCE.md`: claim-to-file map.
- `artifact/CLAIM_SURVIVAL_CARD.md`: supported, scoped, unsupported, and
  non-claims.
- `artifact/INFORMATION_ACCESS_CARD.md`: information-access disclosure.
- `artifact/KNOWN_LIMITATIONS.md`: limitations and non-claims.
- `artifact/REPRODUCIBILITY_STATUS.md`: cached regeneration vs. live reruns.
- `artifact/VERIFICATION_LOG.md`: recorded PASS checks.
- `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`: reusable audit template.

## One-sentence summary

This artifact is a **reviewer-verifiable claim-audit package**: it lets reviewers
trace each paper claim to cached results, regeneration scripts, provenance
checks, information-access disclosures, and explicit non-claims.
