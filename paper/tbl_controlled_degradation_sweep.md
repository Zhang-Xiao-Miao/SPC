# Controlled Prior-Quality Degradation Sweep

This is a diagnostic sweep over a fixed MBPP+ slice. It treats degraded structural priors as boundary evidence, not as causal proof or a deployable prior-quality estimator.

- Slice size: `50` from `MBPP+100`
- Candidate budget: `8`
- Seed: `1`
- Backend: `deepseek-ai/deepseek-coder-6.7b-instruct` via `vllm_openai`

| Setting | Solved | Net | Improved | Regressed | Harm | Mean Diagnostic Fidelity | High Coverage | Compile-Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_prior | 39/50 | +0 | 0 | 0 | NA | 0.000 | 0.000 | 0.350 |
| intended_multi | 39/50 | +0 | 0 | 0 | NA | 0.182 | 0.100 | 0.365 |
| drop_api_tags | 40/50 | +1 | 2 | 1 | 0.333 | 0.106 | 0.060 | 0.362 |
| drop_control_flow_tags | 39/50 | +0 | 0 | 0 | NA | 0.123 | 0.080 | 0.370 |
| drop_data_structure_tags | 39/50 | +0 | 0 | 0 | NA | 0.139 | 0.040 | 0.352 |
| replace_25 | 39/50 | +0 | 0 | 0 | NA | 0.091 | 0.020 | 0.370 |
| replace_50 | 39/50 | +0 | 1 | 1 | 0.500 | 0.091 | 0.020 | 0.357 |
| replace_75 | 39/50 | +0 | 0 | 0 | NA | 0.091 | 0.020 | 0.378 |
| random_prior | 37/50 | -2 | 0 | 2 | 1.000 | 0.048 | 0.000 | 0.448 |
| corrupted_prior | 40/50 | +1 | 1 | 0 | 0.000 | 0.289 | 0.140 | 0.388 |


Boundary: include positive, negative, and noisy rows. Do not present this sweep as a causal proof or as a replacement for the main prior-quality response audit.
