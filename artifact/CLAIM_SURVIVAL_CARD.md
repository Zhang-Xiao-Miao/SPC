# Claim Survival Card

Use this card to record which structural-prior claims survive a diagnostic audit. The goal is not to make every row positive; the goal is to preserve supported claims and make unsupported claims explicit.

| Claim level | Candidate claim | Audit result | Evidence | Boundary | Survives? |
| --- | --- | --- | --- | --- | --- |
| C0 | Operational pipeline gain | Supported | `167/224 -> 184/224` | Entangles structural conditioning and selection opportunity. | Yes, operational only |
| C1 | Structure-attributable fair-budget diagnostic gain | Supported with scope | `178.67 -> 185.00` | Fixed code-aware `syntax_aware` episodes with diagnostic `MBR-exec`. | Scoped |
| C2 | Deployable prompt-only structural retrieval | Unsupported | Full `MBPP+224` prompt-only structural rerun: `179.33` vs `177.67` | Current prompt-only retriever does not reproduce the main positive effect. | No |
| C3 | Quality-conditioned interpretation | Diagnostic support | Medium/high-fidelity code-aware bins are positive; full prompt-only high-fidelity coverage is low. | `structure_fidelity` is retrospective and reference-code-based. | Diagnostic |
| C4 | Broad transfer, backend invariance, strongest-method claim | Unsupported | External/backend rows are mixed, including weak-backend regressions. | Boundary evidence only. | No |

## Writing Rules

- Positive diagnostic rows must retain their information-access and selector boundaries.
- Prompt-only negative rows should remain visible as boundary evidence.
- Prior-quality response may support a quality-conditioned interpretation, but it is not causal proof or a deployable quality estimator.
- External/backend rows instantiate the audit pattern; they are not broad-transfer or backend-invariance evidence.
