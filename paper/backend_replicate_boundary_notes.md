# Backend Replicate Boundary Notes

This note documents the Granite and StarCoder2 backend-boundary reanalysis. It is included as paper-facing artifact evidence for replicate-sensitive backend audit reporting, not as a new main result, broad cross-backend claim, or backend-invariance claim.

## Shared Protocol

- Dataset / slice: `MBPP+100`
- Episodes: `data/episodes/mbppplus_test100_episodes.jsonl`
- Retrieval: fixed code-aware `syntax_aware`
- Candidate budget: `8`
- Prior condition: `multi_candidate`, `num_prior_candidates = 2`
- Gate: `gate_mode = none`
- Rerank: diagnostic `mbr_exec`
- Temperature: `0.4`
- Max new tokens: `200`
- Timeout: `8`

Important caveat: the pipeline `seed` is not passed into the vLLM OpenAI payload. Seed labels should therefore be interpreted as stochastic replicate labels rather than deterministic generation seeds.

## Aggregate Results

| Backend | Replicate Set | `no_prior + MBR` | `multi_prior + MBR` | Solved Delta | Candidate-Pass Delta |
| --- | --- | ---: | ---: | ---: | ---: |
| Granite 8B instruct/chat | original 2 reps | 152/200 | 151/200 | -1 | +17 |
| Granite 8B instruct/chat | new 2 reps | 144/200 | 152/200 | +8 | +30 |
| Granite 8B instruct/chat | combined 4 reps | 296/400 | 303/400 | +7 | +47 |
| StarCoder2-7B completion | original 2 reps | 146/200 | 147/200 | +1 | +18 |
| StarCoder2-7B completion | new 2 reps | 136/200 | 153/200 | +17 | +41 |
| StarCoder2-7B completion | combined 4 reps | 282/400 | 300/400 | +18 | +59 |

Granite is the cleaner non-Qwen/non-DeepSeek supplemental backend because it uses an instruction/chat serving path. Its four-replicate result is modest-positive but noisy. StarCoder2 is a completion-style serving boundary because the local tokenizer does not provide a chat template and the pipeline falls back to `/completions`; it should not be treated as a clean instruction-backend replication.

## Quality-Bin Decomposition

Granite combined four replicates:

| Fidelity Bin | N | `no_prior` | `multi_prior` | Delta | Candidate-Pass Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| low `<0.15` | 224 | 184 | 185 | +1 | +22 |
| medium `[0.15,0.50)` | 148 | 93 | 98 | +5 | +20 |
| high `>=0.50` | 28 | 19 | 20 | +1 | +5 |

StarCoder2 combined four replicates:

| Fidelity Bin | N | `no_prior` | `multi_prior` | Delta | Candidate-Pass Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| low `<0.15` | 224 | 181 | 192 | +11 | +52 |
| medium `[0.15,0.50)` | 148 | 85 | 92 | +7 | +6 |
| high `>=0.50` | 28 | 16 | 16 | +0 | +1 |

## Filter Attempts

Two simple Granite filter variants were tried for transparency:

- `drop_api_tags`
- `unsupported_api_gate`

They did not beat the same-round always-on `multi_prior` rerun:

| Setting | Aggregate |
| --- | ---: |
| no prior rerun | 144/200 |
| always-on multi-prior rerun | 152/200 |
| `drop_api_tags` | 146/200 |
| `unsupported_api_gate` | 147/200 |

These filters are not part of the canonical claim set and should not be described as deployable prior-quality gates.

## Raw Result Inventory

Granite original:

- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`

Granite new:

- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_drop_api_tags_mbrexec_budget8_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_drop_api_tags_mbrexec_budget8_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_unsupported_api_gate_mbrexec_budget8_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_unsupported_api_gate_mbrexec_budget8_seed2.json`

StarCoder2 original:

- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`

StarCoder2 new:

- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed2.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed2.json`

## Supported Interpretation

These checks support replicate-aware backend audit reporting: for backend-level claims, report stochastic replicate count, whether generation seeds are deterministic, candidate-level pass movement, paired changed outcomes, and serving format.

They do not support backend invariance, broad cross-backend claims, or a claim that simple prior-quality filters solve deployable prior selection.
