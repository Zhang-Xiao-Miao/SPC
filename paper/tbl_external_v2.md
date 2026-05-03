# External Evidence V2

The external evaluation should be read as a qualified protocol package, not as a broad-transfer section. `HumanEval+164` remains the full-benchmark non-degradation anchor; `HumanEval+50` is mixed across two DeepSeek seeds, and `BigCodeBench-Hard compatible50` adds a slice-level compatibility check under the same matched-budget logic.

Rerun status:

- `HumanEval+164` and `HumanEval+50` are rerunnable from the packaged repo inputs.
- `BigCodeBench-Hard compatible30/50` are rerunnable after reconstructing the processed compatibility slices and episodes from upstream sources.
- The compatibility-slice preparation step itself is not fully self-contained unless a local BigCodeBench dataset cache is available; the packaged artifact therefore treats slice preparation as provenance material and slice evaluation as rerunnable.

| Evaluation | Setting | Passed | Interpretation |
| --- | --- | ---: | --- |
| HumanEval+164 full fallback | `no_prior + MBR` | 138/164 | full external baseline |
| HumanEval+164 full fallback | `best_structure + MBR` | 138/164 | non-degradation, not positive transfer gain |
| HumanEval+50 DeepSeek slice, seed 1 | `no_prior + MBR` | 42/50 | medium-size external anchor on the supplementary backend |
| HumanEval+50 DeepSeek slice, seed 1 | `multi_prior + MBR` | 44/50 | seed-1 positive slice result |
| HumanEval+50 DeepSeek slice, seed 2 | `no_prior + MBR` | 44/50 | second stochastic replicate |
| HumanEval+50 DeepSeek slice, seed 2 | `multi_prior + MBR` | 41/50 | seed-2 regression reverses the seed-1 positive result |
| HumanEval+50 DeepSeek two-seed aggregate | `no_prior + MBR` vs `multi_prior + MBR` | 86/100 vs 85/100 | mixed / near-neutral boundary evidence; not transfer |
| BigCodeBench-Hard compatible30 DeepSeek | `no_prior + MBR` | 14/30 | compatibility-filtered modern external feasibility check |
| BigCodeBench-Hard compatible30 DeepSeek | `multi_prior + MBR` | 11/30 | negative intermediate slice; shows modern-slice sensitivity |
| BigCodeBench-Hard compatible50 DeepSeek | `no_prior + MBR` | 22/50 | larger compatibility-filtered modern slice |
| BigCodeBench-Hard compatible50 DeepSeek | `multi_prior + MBR` | 23/50 | small positive delta on a larger modern slice |

Takeaway: the paper now has more complete external boundary evidence than the earlier `compatible20` package, but it remains deliberately qualified. The full external benchmark supports non-degradation, HumanEval+50 with DeepSeek is mixed across two seeds (`42/50 -> 44/50` for seed 1, `44/50 -> 41/50` for seed 2, aggregate `86/100` vs `85/100`), and the larger BigCodeBench-Hard compatibility slice shows that modern external behavior is measurable but still slice-sensitive. None of these rows should be paraphrased as broad transfer.
