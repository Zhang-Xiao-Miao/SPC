# Bad Prior Delta Types

All numbers below compare each bad-prior setting against `no_prior + MBR` on the same `MBPP+224 fair-budget` seed. This is a compact reviewer-facing decomposition, not a new benchmark. The current canonical package includes seed-complete bad-prior comparisons for seeds `1,2,3`.

| Setting | Seeds | Improved Mean+/-Std | Regressed Mean+/-Std | Unchanged Mean+/-Std | All Compile Fail Mean+/-Std | Compiled But Failed Tests Mean+/-Std | Best Timeout Mean+/-Std | Rerank Miss Mean+/-Std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| random_prior | 1,2,3 | 8.33 +/- 0.58 | 14.67 +/- 0.58 | 201.00 +/- 1.00 | 14.00 +/- 1.00 | 0.00 +/- 0.00 | 0.00 +/- 0.00 | 0.00 +/- 0.00 |
| corrupted_prior | 1,2,3 | 11.33 +/- 1.15 | 16.67 +/- 0.58 | 196.00 +/- 1.00 | 15.67 +/- 1.15 | 0.00 +/- 0.00 | 0.67 +/- 0.58 | 0.00 +/- 0.00 |

The current multi-seed package shows that `all_compile_fail` remains the dominant regression type, but other failure modes also appear in some seeds. The mechanism claim should therefore stay focused on proposal-quality degradation rather than on reranker-only error.
