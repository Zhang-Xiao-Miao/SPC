# Prior-Quality Response Curve Source

This markdown file provides a figure-source table for plotting quality-response curves. The x-axis is the fidelity threshold, and the y-axis can be `Net Delta` or `Harm Rate`.

Caption for manuscript use: The curve is retrospective and reference-code-based. It is a diagnostic response audit, not a deployable quality estimator.

| Regime | Setting | Fidelity >= Threshold | Coverage | Net Delta | Harm Rate |
| --- | --- | ---: | ---: | ---: | ---: |
| code-aware `syntax_aware` | single_prior | 0.10 | 0.433 | +10 | 0.273 |
| code-aware `syntax_aware` | single_prior | 0.15 | 0.397 | +10 | 0.273 |
| code-aware `syntax_aware` | single_prior | 0.25 | 0.277 | +11 | 0.000 |
| code-aware `syntax_aware` | single_prior | 0.50 | 0.094 | +3 | 0.000 |
| code-aware `syntax_aware` | multi_prior | 0.10 | 0.504 | +17 | 0.207 |
| code-aware `syntax_aware` | multi_prior | 0.15 | 0.469 | +17 | 0.207 |
| code-aware `syntax_aware` | multi_prior | 0.25 | 0.339 | +16 | 0.100 |
| code-aware `syntax_aware` | multi_prior | 0.50 | 0.107 | +4 | 0.250 |
| code-aware `syntax_aware` | random_prior | 0.10 | 0.182 | -7 | 0.706 |
| code-aware `syntax_aware` | random_prior | 0.15 | 0.164 | -7 | 0.733 |
| code-aware `syntax_aware` | random_prior | 0.25 | 0.115 | -7 | 0.818 |
| code-aware `syntax_aware` | random_prior | 0.50 | 0.015 | +0 | 0.500 |
| code-aware `syntax_aware` | corrupted_prior | 0.10 | 0.750 | -9 | 0.563 |
| code-aware `syntax_aware` | corrupted_prior | 0.15 | 0.750 | -9 | 0.563 |
| code-aware `syntax_aware` | corrupted_prior | 0.25 | 0.747 | -9 | 0.563 |
| code-aware `syntax_aware` | corrupted_prior | 0.50 | 0.103 | -5 | 0.778 |
| prompt-only `prompt_structural` | single_prior | 0.10 | 0.205 | -6 | 0.714 |
| prompt-only `prompt_structural` | single_prior | 0.15 | 0.192 | -6 | 0.714 |
| prompt-only `prompt_structural` | single_prior | 0.25 | 0.116 | +1 | 0.429 |
| prompt-only `prompt_structural` | single_prior | 0.50 | 0.009 | +0 | NA |
| prompt-only `prompt_structural` | multi_prior | 0.10 | 0.214 | -4 | 0.667 |
| prompt-only `prompt_structural` | multi_prior | 0.15 | 0.201 | -4 | 0.667 |
| prompt-only `prompt_structural` | multi_prior | 0.25 | 0.129 | +3 | 0.200 |
| prompt-only `prompt_structural` | multi_prior | 0.50 | 0.009 | +0 | NA |
