# Replicate-Sensitive Backend Boundary Checks on MBPP+100

These additional backend checks use fixed code-aware `syntax_aware` episodes, candidate budget `8`, diagnostic `MBR-exec`, `gate_mode=none`, and the same `MBPP+100` slice. The pipeline `seed` label is not passed into the vLLM OpenAI payload, so replicate labels should be read as stochastic replicate labels rather than deterministic generation seeds.

| Backend | Serving | Reps | `no_prior + MBR` | `multi_prior + MBR` | Solved Delta | Candidate-Pass Delta | Role |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Granite 8B code instruct | chat | 4 | 296/400 | 303/400 | +7 | +47 | Cleaner non-Qwen/non-DeepSeek instruct backend; modest-positive but noisy. |
| StarCoder2-7B | completions | 4 | 282/400 | 300/400 | +18 | +59 | Completion-style serving boundary; positive after more replicates but prompt/backend mismatch remains. |

Caption: Additional backend boundary checks on `MBPP+100`. Granite and StarCoder2 show that two stochastic replicates can be too brittle for backend-level structural-prior claims. Four-replicate aggregation is positive for both backends and candidate-level pass deltas are positive, but Granite remains modest/noisy and StarCoder2 is a completion-style serving boundary. These results support replicate-aware audit reporting, not backend invariance.
