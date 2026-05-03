# Cross-Model Evidence V2

Cross-model results should be presented as a portability boundary check rather than as a backend-invariance demonstration.

Seed note:

- Qwen row: seeds `1,2`
- DeepSeek row: seeds `1,2`
- StarCoder2-7B row: original two replicate labels `1,2`; served through vLLM completions because the local tokenizer has no chat template. See `paper/tbl_backend_replicate_boundary.md` for the four-replicate update.
- weak backend row: GPU seeds `1,2`, boundary check rather than headline comparison

| Backend | Dataset | `no_prior + MBR` | `single_prior + MBR` | `multi_prior + MBR` | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| `vllm_openai / Qwen2.5-Coder-7B-Instruct` | `MBPP+100` | `81.50 +/- 0.71` | `83.50 +/- 0.71` | `82.50 +/- 0.71` | primary strong backend remains modest-positive across two seeds; `single_prior` is slightly above `multi_prior`, but both stay above `no_prior` on average |
| `vllm_openai / deepseek-coder-6.7b-instruct` | `MBPP+100` | `77.00 +/- 0.00` | `77.50 +/- 0.71` | `78.50 +/- 0.71` | same-scale second backend remains modest-positive across two seeds, with the clearest gain on `multi_prior` |
| `vllm_openai completions / bigcode/starcoder2-7b` | `MBPP+100` | `73.00 +/- 1.41` | `71.50 +/- 0.71` | `73.50 +/- 2.12` | completion-style StarCoder2-7B is mixed: `single_prior` regresses in both seeds, while `multi_prior` is `-2,+3`, yielding a near-neutral aggregate |
| `hf_causal / bigcode-tiny-starcoder-py` on GPU | `MBPP+100` | `16.50 +/- 3.54` | not evaluated | `10.50 +/- 3.54` | weak backend boundary check regresses under `multi_prior` across two GPU seeds |

Takeaway: current evidence includes two instruction-style same-scale code backends with two-seed support on `MBPP+100`, and both retain only modest gains under the fair-budget protocol. The original two-replicate StarCoder2-7B completion row is mixed and near-neutral, but the four-replicate backend-boundary table shifts StarCoder2 positive while preserving its serving-format caveat. The weak StarCoder-family backend regresses in both seeds. The right claim remains backend-sensitive and replicate-aware audit reporting, not backend invariance.
