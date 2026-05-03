# Retrospective Prior-Quality Response Audit of the Information-Access Boundary

This table stratifies paired outcomes by the diagnostic `structure_fidelity` field already recorded in the raw run files by `plan_b/pipeline.py`. The audit script reads that stored field; it does not recompute retrieval, rerun generation, tune prompts, tune retrieval, filter episodes, or compute new `structure_fidelity` values for the paper table. The metric compares query reference-code structure with the prior summary through API-call, control-flow, and data-structure overlap. It is a retrospective audit metric, not a deployable prior-construction method.

Table caption for manuscript use: This table is retrospective and reference-code-based. It is not a deployable prior-quality estimator and is not used to tune retrieval, prompts, generation, or episode selection.

Bins are fixed in the audit script: `low < 0.15`, `0.15 <= medium < 0.50`, and `high >= 0.50`. These cut points match the earlier project heuristic in `scripts/54_train_usefulness_v2.py` (`fidelity < 0.15` and `fidelity >= 0.5`) and are reported for interpretability, not model selection.

Reported quantities: `Coverage = N / total_N_for_condition`, `Net Delta = improved - regressed`, and `Harm Rate = regressed / (improved + regressed)`, with `NA` when there are no changed outcomes.

## Code-aware diagnostic `syntax_aware` MBPP+224

- Result root: `results/mbpp224_fair_budget`
- Baseline: `no_prior`
- Seeds: `1, 2, 3`

| Regime | Setting | Fidelity Bin | N | Coverage | Improved | Regressed | Unchanged | Net Delta | Harm Rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| code-aware `syntax_aware` | single_prior | low | 405 | 0.603 | 9 | 10 | 386 | -1 | 0.526 |
| code-aware `syntax_aware` | single_prior | medium | 204 | 0.304 | 13 | 6 | 185 | +7 | 0.316 |
| code-aware `syntax_aware` | single_prior | high | 63 | 0.094 | 3 | 0 | 60 | +3 | 0.000 |
| code-aware `syntax_aware` | multi_prior | low | 357 | 0.531 | 7 | 5 | 345 | +2 | 0.417 |
| code-aware `syntax_aware` | multi_prior | medium | 243 | 0.362 | 17 | 4 | 222 | +13 | 0.190 |
| code-aware `syntax_aware` | multi_prior | high | 72 | 0.107 | 6 | 2 | 64 | +4 | 0.250 |
| code-aware `syntax_aware` | random_prior | low | 562 | 0.836 | 21 | 33 | 508 | -12 | 0.611 |
| code-aware `syntax_aware` | random_prior | medium | 100 | 0.149 | 3 | 10 | 87 | -7 | 0.769 |
| code-aware `syntax_aware` | random_prior | high | 10 | 0.015 | 1 | 1 | 8 | +0 | 0.500 |
| code-aware `syntax_aware` | corrupted_prior | low | 168 | 0.250 | 3 | 10 | 155 | -7 | 0.769 |
| code-aware `syntax_aware` | corrupted_prior | medium | 435 | 0.647 | 29 | 33 | 373 | -4 | 0.532 |
| code-aware `syntax_aware` | corrupted_prior | high | 69 | 0.103 | 2 | 7 | 60 | -5 | 0.778 |

Outcome-level fidelity separation, without binning:

| Setting | Improved N | Improved Fidelity | Regressed N | Regressed Fidelity | Unchanged N | Unchanged Fidelity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| single_prior | 25 | 0.253 | 16 | 0.074 | 631 | 0.142 |
| multi_prior | 30 | 0.311 | 11 | 0.168 | 631 | 0.163 |
| random_prior | 25 | 0.054 | 44 | 0.090 | 603 | 0.053 |
| corrupted_prior | 34 | 0.320 | 50 | 0.315 | 588 | 0.277 |

Threshold sensitivity for fidelity-qualified subsets:

| Setting | Fidelity >= Threshold | N | Coverage | Improved | Regressed | Unchanged | Net Delta | Harm Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| single_prior | 0.10 | 291 | 0.433 | 16 | 6 | 269 | +10 | 0.273 |
| single_prior | 0.15 | 267 | 0.397 | 16 | 6 | 245 | +10 | 0.273 |
| single_prior | 0.25 | 186 | 0.277 | 11 | 0 | 175 | +11 | 0.000 |
| single_prior | 0.50 | 63 | 0.094 | 3 | 0 | 60 | +3 | 0.000 |
| multi_prior | 0.10 | 339 | 0.504 | 23 | 6 | 310 | +17 | 0.207 |
| multi_prior | 0.15 | 315 | 0.469 | 23 | 6 | 286 | +17 | 0.207 |
| multi_prior | 0.25 | 228 | 0.339 | 18 | 2 | 208 | +16 | 0.100 |
| multi_prior | 0.50 | 72 | 0.107 | 6 | 2 | 64 | +4 | 0.250 |
| random_prior | 0.10 | 122 | 0.182 | 5 | 12 | 105 | -7 | 0.706 |
| random_prior | 0.15 | 110 | 0.164 | 4 | 11 | 95 | -7 | 0.733 |
| random_prior | 0.25 | 77 | 0.115 | 2 | 9 | 66 | -7 | 0.818 |
| random_prior | 0.50 | 10 | 0.015 | 1 | 1 | 8 | +0 | 0.500 |
| corrupted_prior | 0.10 | 504 | 0.750 | 31 | 40 | 433 | -9 | 0.563 |
| corrupted_prior | 0.15 | 504 | 0.750 | 31 | 40 | 433 | -9 | 0.563 |
| corrupted_prior | 0.25 | 502 | 0.747 | 31 | 40 | 431 | -9 | 0.563 |
| corrupted_prior | 0.50 | 69 | 0.103 | 2 | 7 | 60 | -5 | 0.778 |

## Prompt-only `prompt_structural` MBPP+224

- Result root: `results/prompt_only_structural_mbpp224_fair_budget`
- Baseline: `no_prior`
- Seeds: `1, 2, 3`

| Regime | Setting | Fidelity Bin | N | Coverage | Improved | Regressed | Unchanged | Net Delta | Harm Rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| prompt-only `prompt_structural` | single_prior | low | 543 | 0.808 | 12 | 23 | 508 | -11 | 0.657 |
| prompt-only `prompt_structural` | single_prior | medium | 123 | 0.183 | 4 | 10 | 109 | -6 | 0.714 |
| prompt-only `prompt_structural` | single_prior | high | 6 | 0.009 | 0 | 0 | 6 | +0 | NA |
| prompt-only `prompt_structural` | multi_prior | low | 537 | 0.799 | 14 | 15 | 508 | -1 | 0.517 |
| prompt-only `prompt_structural` | multi_prior | medium | 129 | 0.192 | 4 | 8 | 117 | -4 | 0.667 |
| prompt-only `prompt_structural` | multi_prior | high | 6 | 0.009 | 0 | 0 | 6 | +0 | NA |

Outcome-level fidelity separation, without binning:

| Setting | Improved N | Improved Fidelity | Regressed N | Regressed Fidelity | Unchanged N | Unchanged Fidelity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| single_prior | 16 | 0.083 | 33 | 0.061 | 623 | 0.054 |
| multi_prior | 18 | 0.074 | 23 | 0.063 | 631 | 0.059 |

Threshold sensitivity for fidelity-qualified subsets:

| Setting | Fidelity >= Threshold | N | Coverage | Improved | Regressed | Unchanged | Net Delta | Harm Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| single_prior | 0.10 | 138 | 0.205 | 4 | 10 | 124 | -6 | 0.714 |
| single_prior | 0.15 | 129 | 0.192 | 4 | 10 | 115 | -6 | 0.714 |
| single_prior | 0.25 | 78 | 0.116 | 4 | 3 | 71 | +1 | 0.429 |
| single_prior | 0.50 | 6 | 0.009 | 0 | 0 | 6 | +0 | NA |
| multi_prior | 0.10 | 144 | 0.214 | 4 | 8 | 132 | -4 | 0.667 |
| multi_prior | 0.15 | 135 | 0.201 | 4 | 8 | 123 | -4 | 0.667 |
| multi_prior | 0.25 | 87 | 0.129 | 4 | 1 | 82 | +3 | 0.200 |
| multi_prior | 0.50 | 6 | 0.009 | 0 | 0 | 6 | +0 | NA |

## Quality-Conditioned Takeaway

1. Average deltas are insufficient: a prior condition may look weak because it rarely constructs high-fidelity priors.
2. Coverage matters: the full prompt-only rerun has very low high-fidelity coverage.
3. Harm matters: low-quality or misleading priors can increase regressions.
4. The audit is retrospective: `structure_fidelity` uses reference-code structure and is not a deployable estimator.

## Interpretation

- In the fixed code-aware `syntax_aware` diagnostic episodes, intended priors show positive net deltas in medium- and high-fidelity bins. This supports a quality-conditioned diagnostic claim rather than a broad structural-prior method claim.
- The unbinned outcome-level fidelity separation provides the same cautionary direction for the main intended prior: in code-aware `multi_prior`, improved outcomes have higher diagnostic fidelity than regressed outcomes (`0.311` vs `0.168`).
- Threshold sensitivity is reported over multiple fixed cutoffs (`0.10`, `0.15`, `0.25`, and `0.50`) to reduce dependence on a single bin boundary. This is still diagnostic stratification, not a threshold-tuned decision rule.
- In the full prompt-only `prompt_structural` rerun, diagnostic-fidelity coverage is much lower and high-fidelity cases are rare. The non-positive prompt-only result is consistent with the boundary claim that this retriever did not construct high-quality priors on full MBPP+224.
- Bad-prior conditions should not be interpreted through fidelity alone: corrupted priors can preserve surface structural overlap while still being misleading. They remain diagnostic stress tests rather than deployable priors.
