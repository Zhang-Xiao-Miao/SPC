# External Protocol

The external story should be written as a qualified protocol contribution rather than as a broad-transfer success claim.

## Why HumanEval+ Remains The Fallback Anchor

`HumanEval+164` is the cleanest full external benchmark currently aligned with the Plan B function-generation protocol. Under fixed candidate budget, it supports non-degradation, not a positive transfer gain.

## Why BigCodeBench-Hard Is A Qualified Modern Slice

The `BigCodeBench-Hard` result is compatibility-filtered rather than benchmark-complete. The filter is environment-driven: only tasks whose declared dependency roots can be imported in the current environment are kept. This makes the slice reproducible and honest, but it also narrows the admissible claim.

In the current environment, this compatibility rule admits `66` tasks, which made it possible to expand the earlier `compatible20` check to `compatible30` and `compatible50` slices without changing the protocol. The larger slice is more informative than the original 20-task check, but it is still not a benchmark-complete external result.

## Allowed Claim

The combined external package supports:

- qualified feasibility on a modern benchmark slice
- mixed `HumanEval+50` DeepSeek boundary evidence across two seeds, with aggregate `86/100` versus `85/100`
- a small slice-level positive row on `BigCodeBench-Hard compatible50` for the active DeepSeek backend
- non-degradation on a full external benchmark

It does not support:

- broad modern benchmark transfer
- benchmark-wide modern external generality
External reproducibility status should be stated explicitly:

- `HumanEval+164` and `HumanEval+50` can be rerun after reconstructing the expected benchmark data/episode layout from upstream sources.
- `BigCodeBench-Hard compatible30/50` can be rerun after reconstructing processed examples plus episodes from upstream sources.
- The compatibility-filtering step depends on a local `BigCodeBench-Hard` dataset cache unless one reconstructs the processed slices separately.
