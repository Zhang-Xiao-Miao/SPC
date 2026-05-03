# Audit Reporting Checklist

This checklist is the reusable E&D reporting object extracted from SPC-Audit: Structural-Prior Claim Audit. It is intended for structural-prior claims in execution-evaluated code generation, not as a new benchmark or deployable method.

## Required Items

| Item | What To Report | Why It Matters |
| --- | --- | --- |
| Candidate budget | Total generated candidates per query and how budget is split across prior variants. | Separates structural conditioning from extra proposal opportunity. |
| Execution-call accounting | Number of candidate executions available to each condition. | Prevents attributing execution-selection opportunity to the prior. |
| Prompt-token accounting | Prompt-token totals or a clear statement that they are not matched. | Avoids overclaiming full compute equality. |
| Information access | Query-side and support-side fields used by retrieval, prompting, selection, and evaluation. | Distinguishes prompt-only, code-aware, oracle-derived, and test-aware evidence. |
| Selection status | Whether selection is deployable, diagnostic, same-test, public-test, or oracle-like. | Determines how solved-count gains should be interpreted. |
| Prompt-only boundary control | A retrieval/control condition that uses no query solution code. | Tests whether code-aware diagnostic findings transfer to cleaner settings. |
| Bad-prior control | Random, corrupted, or otherwise misleading priors with the same budget and selector. | Tests whether the selector masks prior harm. |
| Paired directionality | Improved/regressed/unchanged outcomes, preferably with task-clustered reporting. | Avoids relying only on aggregate pass counts or pooled p-values. |
| Replicate sensitivity | For backend-level claims, report stochastic replicate count, whether generation seeds are deterministic, candidate-level pass movement, paired changed outcomes, and serving format. | Prevents over-reading brittle two-replicate backend rows as stable positive, neutral, or negative evidence. |
| Prior-quality response | Optional when reference or trusted structure is available; report coverage, bin-level net delta, harm rate, outcome-level fidelity separation, and threshold sensitivity. | Turns prior quality into an inspectable response variable rather than a post-hoc explanation. |
| Claim survival hierarchy | Label each candidate claim as supported, supported with scope, diagnostic-only, unsupported, or an explicit non-claim. | Turns negative and mixed results into an auditable claim boundary rather than a hidden weakness. |
| Explicit non-claims | Unsupported deployment, backend-invariance, broad-transfer, strongest-method, and safety interpretations. | Prevents accidental overgeneralization. |

The minimum reusable contribution is this reporting checklist plus a claim-to-evidence artifact that makes the reported items inspectable. It is a reporting pattern instantiated in this setting, not a general audit framework and not a requirement to use this paper's exact selector or benchmark.

## Optional Diagnostic Items

| Item | When To Use | Boundary |
| --- | --- | --- |
| Prior-quality response audit details | Use when a reference solution or trusted structure source is available for retrospective analysis. Include the complete table and machine-readable JSON when possible. | Diagnostic only; not a deployable estimator unless it avoids reference-only information. |
| Threshold sensitivity | Use when a quality audit bins examples by fidelity or confidence. | Reduces dependence on one cutoff, but does not prove causality. |
| External/backend slices | Use to identify transfer and backend boundaries. | Qualified evidence unless benchmark-complete and adequately replicated. |
| Reproducibility package | Include source, processed inputs or preparation scripts, raw outputs, table scripts, and hashes. | Must distinguish full reruns from table regeneration over cached outputs. |

## Plan B Instantiation

Plan B instantiates all required items. Its key boundary is that the main `syntax_aware` result is fixed code-aware diagnostic evidence and `MBR-exec` is same-test diagnostic execution-selection. Therefore, the supported conclusion is about warranted structural-prior claims under SPC-Audit, not about deployable prompt-only structural retrieval.

Future work can adopt the required checklist without using reference-code structure. In that case, prior-quality auditing should be omitted or replaced with a clearly labeled non-reference diagnostic; it should not be implied by the checklist unless the required information is available.
