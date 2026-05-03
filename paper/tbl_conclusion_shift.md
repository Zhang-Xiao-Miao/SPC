# Conclusion Shift Under Fair Evaluation

This table is the paper's E&D centerpiece: it shows that changing the evaluation design changes the scientific interpretation of the same method family.

| Regime | Baseline | Compared Setting | Baseline Solved | Compared Solved | Delta | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Earlier / uncontrolled comparison | syntax-aware / no prior / no rerank | syntax-aware / multi prior / always-on / MBR-exec | 167/224 | 184/224 | +17 | Large absolute gain, but structural conditioning and execution-selection opportunity are entangled. |
| Fair-budget diagnostic comparison | no_prior + MBR | multi_prior + MBR | 178.67 +/- 0.58 | 185.00 +/- 1.73 | +6.33 | Structural priors retain a modest effect in fixed code-aware diagnostic episodes. |
| Full prompt-only structural control | no_prior + MBR | multi_prior + MBR | 179.33 +/- 2.31 | 177.67 +/- 1.53 | -1.67 | Prompt-only structural retrieval does not reproduce the positive main effect on full MBPP+224. |
| Fair-budget bad-prior stress test | no_prior + MBR | random / corrupted prior + MBR | 178.67 | 172.33 / 173.33 | -6.33 / -5.33 | Bad priors remain harmful even under the same diagnostic execution-selection protocol. |

Takeaway: the earlier pipeline supported a strong but entangled "structure helps a lot" reading. The fair-budget diagnostic protocol supports a more precise E&D claim: structural-prior effects are conditioned by evaluation design, information access, and prior quality.
