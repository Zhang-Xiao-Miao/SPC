# Backend Sensitivity Discussion

The current cross-model package still does not justify backend invariance. However, it is now stronger than a single-backend anecdote: both `Qwen2.5-Coder-7B-Instruct` and `deepseek-coder-6.7b-instruct` show a modest positive effect under the same `MBPP+100` fair-budget protocol across two seeds. The Qwen row is `81/84/82` on seed 1 and `82/83/83` on seed 2; the DeepSeek row is `77/77/78` on seed 1 and `77/78/79` on seed 2. Additional Granite and StarCoder2 checks show why backend rows should be replicate-aware: Granite's original two-replicate solved-count row was slightly negative but its four-replicate aggregate is modest-positive (`296/400 -> 303/400`), while StarCoder2 shifts from near-neutral over two replicates to positive over four (`282/400 -> 300/400`). StarCoder2 remains a completion-style serving boundary rather than clean instruction-backend evidence. The much weaker `tiny_starcoder_py` backend regresses. Proposal quality, instruction tuning, stochastic replicate budget, and serving format are therefore part of the causal story, not nuisance variables to be ignored.

Accordingly, the paper should say:

- the effect is backend-sensitive
- current evidence supports qualified same-scale portability across two instruction-style backends, with a two-seed check on Qwen and DeepSeek
- StarCoder-family rows are boundary evidence: StarCoder2-7B becomes positive after additional stochastic replicates but remains completion-style, while the weak tiny backend regresses
- Granite provides a cleaner non-Qwen/non-DeepSeek instruct/chat boundary, but its four-replicate result is modest and noisy
- current evidence still does not support backend invariance
