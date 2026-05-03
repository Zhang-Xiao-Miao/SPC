# DeepSeek Cross-Model Check Across Two Seeds

This table summarizes the same `MBPP+100` fair-budget protocol on the newly added same-scale backend `deepseek-coder-6.7b-instruct`. It is supporting evidence for qualified portability, not a headline benchmark claim.

| Seed | `no_prior + MBR` | `single_prior + MBR` | `multi_prior + MBR` | Interpretation |
| --- | ---: | ---: | ---: | --- |
| 1 | 77/100 | 77/100 | 78/100 | modest positive effect survives on the second same-scale backend |
| 2 | 77/100 | 78/100 | 79/100 | direction remains modest-positive under a second seed |

Takeaway: on `deepseek-coder-6.7b-instruct`, the fair-budget structure effect does not collapse across seeds. The effect remains small, but the ordering is stable enough to support qualified same-scale portability.
