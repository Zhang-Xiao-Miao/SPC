# External Slice Notes

This artifact includes three external packages:

- `HumanEval+164` as the full-benchmark fallback external check
- `HumanEval+50` as a medium-size external slice on the active DeepSeek backend, now with seeds `1,2`
- `BigCodeBench-Hard compatible50` as a larger reproducible modern slice

The modern slice is compatibility-filtered rather than benchmark-complete. Tasks are included only when their declared dependency roots are importable in the current environment. The intended claim is qualified feasibility / small slice-level effects, not broad modern benchmark transfer.
The direct review zip includes cached outputs for the external evaluations already cited by the paper. Live reruns require reconstructing the processed slices and episodes from upstream sources. The compatibility-filtering preparation step for `BigCodeBench-Hard` remains provenance-only and should not be described as fully regenerable from the original upstream benchmark source.
DeepSeek-based `HumanEval+50` results are mixed across seeds `1,2` and should be cited as qualified, slice-sensitive boundary evidence rather than as broad-transfer evidence.
