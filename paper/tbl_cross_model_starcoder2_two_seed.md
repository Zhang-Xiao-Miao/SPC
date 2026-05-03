# StarCoder2-7B Two-Seed Boundary Check

This row uses the same `MBPP+100`, `syntax_aware`, candidate-budget-8, diagnostic `MBR-exec` protocol as the Qwen and DeepSeek cross-model checks. The local `bigcode/starcoder2-7b` checkpoint is served through vLLM completions because its tokenizer does not define a chat template.

Update note: this is the original two-replicate boundary row. The four-replicate update is reported in `paper/tbl_backend_replicate_boundary.md` and should be used for the replicate-sensitive interpretation.

| Seed | `no_prior + MBR` | `single_prior + MBR` | `multi_prior + MBR` | `multi_prior` delta |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 74/100 | 72/100 | 72/100 | -2 |
| 2 | 72/100 | 71/100 | 75/100 | +3 |
| aggregate | `73.00 +/- 1.41` | `71.50 +/- 0.71` | `73.50 +/- 2.12` | near-neutral |

Interpretation: this original two-replicate row is useful boundary evidence. It shows that the same structural-prior protocol is sensitive to backend and serving style: `single_prior` regresses in both seeds, while `multi_prior` is mixed and only `+1` over 200 query-seed outcomes. The later four-replicate update shifts `multi_prior` positive while retaining the completion-style serving caveat.
