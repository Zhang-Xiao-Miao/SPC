# Related Work Notes

This file is a writing aid for the final manuscript. It is intentionally scoped as a structured note, not as the final related-work prose.

## Buckets To Cover

### Code-generation benchmarks and execution-based evaluation

- `MBPP` / `MBPP+`: motivate the main benchmark and the shift from prompt-only to stronger execution-grounded evaluation.
- `HumanEval` / `HumanEval+`: motivate the external non-degradation anchor and slice-based external checks.
- `EvalPlus`: justify the use of strengthened test suites for benchmark conversion and execution-time evaluation.
- `BigCodeBench-Hard`: motivate the compatibility-filtered modern slice as a qualified external stress test rather than a full-transfer claim.

### Inference-time sampling, reranking, and selection

- Execution-based reranking / pass@k style evaluation: position `MBR-exec` as a test-time selection mechanism rather than as a structural prior.
- Minimum Bayes risk style decoding / selection under executable candidates: explain why reranking can dominate the practical gain when candidate budget is fixed.

### Structure-aware or retrieval-augmented code generation

- Structural priors, syntax-aware retrieval, AST-guided prompting, or program-plan conditioning:
  use these to position the paper against prior work that often changes both conditioning and test-time opportunity at once.
- The manuscript should stress that Plan B is not claiming a new best structure method; it is isolating what remains attributable to structure after budget control.
- The current starter bibliography now includes concrete entries for `Syntax-Aware Retrieval Augmented Code Generation` and `StructCoder` as anchors for this bucket.

### Negative auxiliary modules

- Verifier / usefulness / selector style add-ons belong in a short negative-results paragraph or appendix-style discussion.
- The point is not novelty; the point is that plausible patches did not stabilize the fixed-budget claim.

## Writing Guidance

- The related-work section should be organized around evaluation-design confounds, not around a long survey of code LMs.
- Use one paragraph for benchmarks and execution-grounded evaluation, one for structure-aware conditioning, and one for reranking/selection.
- Avoid claiming that prior work was "wrong"; say instead that prior pipelines often entangle conditioning changes with test-time compute changes.

## Must-Cite Objects For Final Pass

- `MBPP`
- `HumanEval`
- `EvalPlus`
- `BigCodeBench`
- one or more execution-based reranking / MBR references
- one or more structure-aware or syntax-aware code-generation references

## Verification Status

- `paper/refs_planb.bib` now contains verified starter entries for `MBPP`, `HumanEval/Codex`, `EvalPlus`, `BigCodeBench`, MBR decoding, syntax-aware retrieval-augmented code generation, and `StructCoder`.
- The bibliography is still intentionally selective rather than exhaustive. Additional related-work expansion is possible, but the core manuscript buckets are no longer empty.
