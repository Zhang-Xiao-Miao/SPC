# Controlled Prior-Quality Degradation Protocol

This protocol was fixed before running the current pilot sweep. The artifact includes a DeepSeek `MBPP+50` pilot in `paper/tbl_controlled_degradation_sweep.md` and `results/degradation_sweep/*.json`. The pilot is secondary diagnostic evidence, not a main result, causal proof, or deployable prior-quality estimator.

## Research Question

If prior quality is treated as the evaluation variable, does controlled degradation of structural priors change net delta and harm rate?

## Fixed Design

- Target full design: `MBPP+100`
- Current pilot: first `50` episodes from the packaged `MBPP+100` episode file
- Target backend: Qwen-family main backend
- Current pilot backend: `deepseek-ai/deepseek-coder-6.7b-instruct` served by local vLLM
- Retrieval: fixed code-aware `syntax_aware` diagnostic episodes
- Candidate budget: `8`
- Target seeds: `1,2` minimum; `1,2,3` only if compute is available before looking at results
- Current pilot seed: `1`
- Selector: same diagnostic `MBR-exec` selector for every condition

## Fixed Conditions

1. `no_prior`
2. intended prior
3. drop API tags
4. drop control-flow tags
5. drop data-structure tags
6. replace 25% structural tags
7. replace 50% structural tags
8. replace 75% structural tags
9. random prior / corrupted prior

The degradation levels are fixed before execution. They must not be changed after seeing results.

## Metrics

- solved tasks
- paired improved / regressed / unchanged outcomes
- stored `structure_fidelity`
- quality coverage
- net delta by fidelity bin
- harm rate
- all-candidate compile-fail rate
- selected-candidate timeout / fail rate

## Inclusion Rules

Include in the main text only if the trend is clear, provenance is clean, and the table is compact. Include in appendix or artifact notes if the result is useful but noisy. Do not include if the result is unstable, requires substantial new explanation, creates tuning suspicion, or threatens the clean claim boundary.

## Reporting Boundary

The current pilot preserves positive, negative, and noisy rows. The allowed claim is that controlled degradation is now instantiated as a secondary diagnostic sweep and that lower-fidelity or bad priors can be audited through net delta, harm rate, and compile-fail rate. It must not be written as causal proof, a deployable quality estimator, or a replacement for the main prior-quality response audit.
