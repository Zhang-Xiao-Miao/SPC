# Contribution And Artifact Summary

This note summarizes the submission contribution in reviewer-facing terms. It is intended to keep the paper and artifact aligned.

## Contribution Position

The paper is an evaluation-design and artifact contribution, not a new structural-prior method and not a new benchmark. The central contribution is **SPC-Audit**, a prior-quality-aware diagnostic audit protocol for structural-prior claims in execution-evaluated code generation.

The reusable pattern has five parts:

1. **Fair-budget diagnostic audit.** Compare prior conditions under matched candidate budget and matched execution-call accounting, while explicitly disclosing information access and selection status.
2. **Information-access boundary controls.** Separate fixed code-aware diagnostic evidence from prompt-only controls and oracle-derived stress tests.
3. **Prior-quality response audit.** Report quality coverage, bin-level net delta, harm rate, outcome-level fidelity separation, and threshold sensitivity instead of only average prior-versus-no-prior solved-task deltas.
4. **Claim survival hierarchy.** Label operational, diagnostic, prompt-only, quality-conditioned, and broad-transfer claims by what assumptions they survive.
5. **Replicate-sensitive backend reporting.** For backend-level claims, report stochastic replicate count, deterministic-seed status, candidate-level pass movement, paired changed outcomes, and serving format.

## What The Artifact Makes Inspectable

| Reviewer Question | Artifact Entry Point |
| --- | --- |
| Which claims are supported, qualified, or unsupported? | `artifact/CLAIM_TO_EVIDENCE.md`, `artifact/KNOWN_LIMITATIONS.md` |
| Can the paper-facing tables be regenerated without live LLM inference? | `artifact/reproduce_main.sh` |
| Is the prompt-only structural matcher fixed and query-prompt-only on the query side? | `artifact/verify_provenance.sh`, `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |
| Does the prior-quality response audit read stored raw-result fields rather than tuning retrieval or filtering episodes? | `artifact/verify_provenance.sh`, `paper/prior_quality_audit_provenance.md`, `scripts/67_make_prior_quality_audit.py` |
| Where are the complete quality-response and threshold-sensitivity tables? | `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_audit.md` |
| What requires live model inference rather than cached-output regeneration? | `artifact/REPRODUCIBILITY_STATUS.md` |
| How can another project reuse the reporting pattern? | `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md` |
| Where is the controlled prior-quality degradation pilot? | `paper/tbl_controlled_degradation_sweep.md`, `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md` |
| Which files are intentionally excluded from the anonymous package? | `artifact/CANONICAL_REVIEWER_PACKAGE.md` |
| Where are small boundary instantiations outside the main table summarized? | `paper/tbl_boundary_instantiations.md` |
| Where are replicate-sensitive Granite and StarCoder2 checks summarized? | `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` |

## Claim Boundary

The artifact supports the following positive claims with scope:

- evaluation design changes the warranted structural-prior conclusion;
- fixed code-aware `syntax_aware` diagnostic episodes show a modest structural-prior effect;
- full `MBPP+224` prompt-only structural retrieval does not reproduce the main positive effect;
- the retrospective prior-quality response audit is consistent with the information-access boundary;
- the controlled degradation pilot gives secondary diagnostic evidence with noisy positive, neutral, and negative rows;
- Granite and StarCoder2 provide replicate-sensitive backend-boundary evidence, not backend invariance;
- bad-prior and backend/external checks define boundaries rather than broad transfer.
- the claim survival hierarchy preserves scoped positive claims while marking prompt-only deployment, broad transfer, backend invariance, and strongest-method claims as unsupported.

The artifact explicitly does not support:

- a strongest-method claim;
- a deployable prompt-only structural-prior method;
- a deployment-time `MBR-exec` selector;
- backend invariance or broad transfer;
- clean StarCoder2 instruction-backend replication;
- a causal mechanism proof from `structure_fidelity`;
- a new benchmark or dataset claim.

## Reviewer Quickstart

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

These commands regenerate paper-facing derived objects from cached outputs, verify matcher and prior-quality provenance, and expose the supported/unsupported claim map.
