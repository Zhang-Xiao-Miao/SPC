# Contribution And Artifact Summary

This reviewer-facing note summarizes the submission contribution and the artifact entry points. The paper is an evaluation-design and artifact contribution, not a new structural-prior method, new benchmark, leaderboard package, or broad-transfer claim.

## Contribution Position

The central contribution is **SPC-Audit**, a prior-quality-aware diagnostic audit protocol for structural-prior claims in execution-evaluated code generation. The main scientific finding is quality-conditioned evaluation: an average prior-vs-no-prior delta is insufficient unless the evaluation also reports prior-quality coverage, net movement by quality band, harm rate, and which claims survive the audit.

The reusable pattern has five parts:

1. **Fair-budget diagnostic audit.** Compare prior conditions under matched candidate budget and matched execution-call accounting, while explicitly disclosing information access and selection status.
2. **Information-access boundary controls.** Separate fixed code-aware diagnostic evidence from prompt-only controls and oracle-derived stress tests.
3. **Prior-quality response audit.** Report quality coverage, bin-level net delta, harm rate, outcome-level fidelity separation, and threshold sensitivity instead of only average prior-versus-no-prior solved-task deltas.
4. **Claim survival hierarchy.** Label operational, diagnostic, prompt-only, quality-conditioned, and broad-transfer claims by what assumptions they survive.
5. **Boundary reporting and explicit non-claims.** External/backend rows, budget sweeps, and controlled-degradation pilots are used to define scope; they are not broad-transfer, backend-invariance, robustness, or deployment claims.

## Reviewer Entry Points

| Reviewer Question | Artifact Entry Point |
| --- | --- |
| What is the expert-edited final paper source? | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex` |
| Which claims are supported, qualified, or unsupported? | `artifact/CLAIM_TO_EVIDENCE.md`, `artifact/KNOWN_LIMITATIONS.md` |
| Can the paper-facing tables be regenerated without live LLM inference? | `artifact/reproduce_main.sh` |
| Is the prompt-only structural matcher fixed and query-prompt-only on the query side? | `artifact/verify_provenance.sh`, `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |
| Does the prior-quality response audit read stored raw-result fields rather than tuning retrieval or filtering episodes? | `artifact/verify_provenance.sh`, `paper/prior_quality_audit_provenance.md`, `scripts/67_make_prior_quality_audit.py` |
| What requires live model inference rather than cached-output regeneration? | `artifact/FULL_REPRODUCTION_GUIDE.md`, `artifact/check_live_rerun_prereqs.sh`, `artifact/REPRODUCIBILITY_STATUS.md` |
| How can another project reuse the reporting pattern? | `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md` |
| Where are small boundary instantiations outside the main table summarized? | `paper/tbl_boundary_instantiations.md` |
| Where are backend-sensitive boundary checks summarized? | `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` |
| Where is the secondary controlled-degradation pilot? | `paper/tbl_controlled_degradation_sweep.md`, `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md` |

## Claim Boundary

The artifact supports scoped positive claims about conclusion shift, fixed code-aware diagnostic gains, prompt-only boundaries, quality-conditioned evaluation, bad-prior harm, and boundary reporting. It does not support a strongest-method claim, deployable prompt-only structural-prior method, deployment-time `MBR-exec` selector, backend invariance, broad transfer, clean StarCoder2 instruction-backend replication, causal mechanism proof from `structure_fidelity`, deployable prior-quality estimation, or a new benchmark claim.

## Quickstart

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```
