# MBPP+224 Paired Outcome Task-Clustered Sensitivity

- Dataset: `MBPP+224`
- Retrieval: `syntax_aware`
- Compared settings: `multi_prior + MBR` vs `no_prior + MBR`
- Candidate budget: `8`
- Seeds: `1,2,3`
- Data source: `results/mbpp224_fair_budget/summary.json` and referenced raw result files.
- Status: statistical sensitivity table for reviewer interpretation.

## Per-Seed Paired Changes

| Seed | Improved | Regressed | Unchanged | Net |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 8 | 3 | 213 | +5 |
| 2 | 10 | 5 | 209 | +5 |
| 3 | 12 | 3 | 209 | +9 |
| pooled query-seed | 30 | 11 | 631 | +19 |

## Task-Clustered Directionality

For each task, seed-level deltas are summed before assigning a task-level direction.

| Task-Level Direction | Count |
| --- | ---: |
| positive net delta | 14 |
| negative net delta | 5 |
| zero net delta | 205 |
| positive-minus-negative | +9 |

Interpretation: the pooled sign-test result should not be treated as if all query-seed outcomes were fully independent. However, the positive direction is still visible after collapsing by task: 14 tasks have positive net deltas, 5 have negative net deltas, and 205 are unchanged. This supports the modest controlled-effect claim while avoiding an overclaim from the pooled p-value.
