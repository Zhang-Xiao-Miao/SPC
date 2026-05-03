# Stats And Cost For Fair-Budget MBPP+224

The paired comparison below uses shared-query outcome changes under matched seed and budget. It is intended as a reviewer-facing sanity check, not as a substitute for the main solved-task table.

| Comparison | Improved | Regressed | Unchanged | Two-Sided Sign-Test p |
| --- | ---: | ---: | ---: | ---: |
| seed1 single vs no_prior | 7 | 5 | 212 | 0.7744 |
| seed1 multi vs no_prior | 8 | 3 | 213 | 0.2266 |
| seed2 single vs no_prior | 9 | 7 | 208 | 0.8036 |
| seed2 multi vs no_prior | 10 | 5 | 209 | 0.3018 |
| seed3 single vs no_prior | 9 | 4 | 211 | 0.2668 |
| seed3 multi vs no_prior | 12 | 3 | 209 | 0.0352 |

Pooled `multi_prior` vs `no_prior` across all three seeds: improved `30`, regressed `11`, unchanged `631`, two-sided sign-test `p=0.0043`.

| Run | Solved | Avg Candidates | Avg Latency (s) | Prompt Tokens | Completion Tokens | Execution Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| seed1 no_prior | 179 | 8.00 | 0.063 | 38261 | 14744 | 1792 |
| seed1 single_prior | 181 | 8.00 | 0.053 | 46078 | 13116 | 1792 |
| seed1 multi_prior | 184 | 8.00 | 0.099 | 46003 | 13118 | 1792 |
| seed2 no_prior | 179 | 8.00 | 0.060 | 38261 | 14643 | 1792 |
| seed2 single_prior | 181 | 8.00 | 0.053 | 46078 | 13172 | 1792 |
| seed2 multi_prior | 184 | 8.00 | 0.099 | 46008 | 13287 | 1792 |
| seed3 no_prior | 178 | 8.00 | 0.063 | 38261 | 14821 | 1792 |
| seed3 single_prior | 183 | 8.00 | 0.054 | 46078 | 13258 | 1792 |
| seed3 multi_prior | 187 | 8.00 | 0.098 | 46012 | 13181 | 1792 |

All compared settings use the same candidate budget and rerank regime, and the `Execution Calls` column is matched within each compared seed.
Prompt-token totals are not equal across prior conditions, so the fairness claim should be written as matched candidate budget plus matched execution-call accounting, not as full compute equality.
