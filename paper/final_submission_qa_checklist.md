# Final Submission QA Checklist

Last updated: 2026-05-01.

This checklist records the current final-stage checks for the NeurIPS 2026 E&D submission line. It is scoped to submission readiness and does not add new scientific claims.

## Claim Safety

- Title stays on claim auditing and diagnostic evaluation.
- Abstract names SPC-Audit and frames the work as an E&D reporting pattern and artifact, not a deployable structural-prior method.
- Introduction states the paper is not a strongest-method, broad-transfer, or deployable prompt-only retrieval claim.
- Claim Audit Card doubles as the Claim Survival Hierarchy and appears before the method section.
- SPC-Audit protocol box appears in the method section.
- Full `MBPP+224` prompt-only structural negative result remains in the main text.
- RQ2 is framed as a retrospective prior-quality response audit.
- RQ3 boundary analyses are compressed into a scope table and do not compete with RQ2 as the main contribution.
- C/D/E additions and Granite/StarCoder2 backend checks are framed as boundary, secondary diagnostic, or replicate-sensitive audit evidence, not broad transfer, backend invariance, or causal proof.
- Limitations state that discounting the retrospective prior-quality audit weakens only the quality-conditioned interpretation, not the core E&D claims.

## Artifact Readiness

- Reviewer quickstart is documented:
  - `bash artifact/reproduce_main.sh`
  - `bash artifact/verify_provenance.sh`
  - `cat artifact/CLAIM_TO_EVIDENCE.md`
  - `cat artifact/KNOWN_LIMITATIONS.md`
- `artifact/reproduce_main.sh` regenerates paper-facing tables and figure-support files from cached outputs.
- `artifact/verify_provenance.sh` checks prompt-only matcher constants, query-side access boundaries, stored `structure_fidelity` fields, and prior-quality response regeneration.
- The canonical anonymous package excludes historical planning drafts, reviewer-attack notes, rebuttal prewrites, and old worklogs.
- The package includes the official `paper/latex/neurips_2026.sty` file required by the current LaTeX source.
- The package includes `paper/contribution_and_artifact_summary.md` and `artifact/VERIFICATION_LOG_2026-04-29.md` as reviewer navigation aids.
- The package includes `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, and `paper/backend_replicate_boundary_notes.md` for Granite/StarCoder2 replicate-sensitive backend checks.
- The package includes reusable reporting resources: `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md`, `artifact/CANONICAL_REVIEWER_PACKAGE.md`, and `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`.

## LaTeX Readiness

- The current source uses `\usepackage[eandd]{neurips_2026}`.
- Author field is anonymous.
- Bibliography compiles through BibTeX.
- Current local build succeeds with project-local TeX Live 2026 and `latexmk`.
- Current PDF is 9 pages in the local draft build.

## Remaining Human QA

- Final checklist answers for the NeurIPS submission form still need to be completed by the authors.
- Reference metadata should receive a final human pass.
- Final artifact link policy should be checked against the exact anonymous submission portal requirements.
