# mbppplus224 prompt_structural Fair-Budget Summary

- Dataset: `mbppplus224`
- Retrieval: `prompt_structural`
- Candidate Budget: `8`
- Execution Budget: `8`
- Rerank: `mbr_exec`
- Source revision: `omitted_for_double_blind_review`

| Setting | Pass Rate Mean±Std | Solved Mean | Solved Range | Avg Latency | Avg Candidates | Prompt Tokens | Completion Tokens | Delta vs no_prior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_prior | 0.8006 ± 0.0103 | 179.33 | [178, 182] | 0.06 | 8.00 | 35516 | 14747 | +0.00 |
| single_prior | 0.7753 ± 0.0026 | 173.67 | [173, 174] | 0.05 | 8.00 | 42353 | 12974 | -5.67 |
| multi_prior | 0.7932 ± 0.0068 | 177.67 | [176, 179] | 0.10 | 8.00 | 42310 | 12968 | -1.67 |

## Paired Changes vs `no_prior`

| Setting | Improved | Regressed | Unchanged | Net | Two-sided sign test |
| --- | ---: | ---: | ---: | ---: | ---: |
| single_prior | 16 | 33 | 623 | -17 | 0.0213 |
| multi_prior | 18 | 23 | 631 | -5 | 0.5327 |

Interpretation: this full prompt-only structural rerun does not reproduce the positive `multi_prior` effect observed in the fixed code-aware `syntax_aware` main table. It is a leakage-risk control and claim-boundary result, not a replacement headline benchmark and not evidence for a deployable prompt-only structural-prior method.
