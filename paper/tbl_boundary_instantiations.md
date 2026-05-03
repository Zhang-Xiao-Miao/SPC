# Boundary Instantiations Beyond The Main MBPP+224 Result

These rows use already packaged raw-result files to document small boundary instantiations beyond the main `MBPP+224` Qwen diagnostic result. They are included to show how the reporting pattern applies outside the primary table, not to claim broad transfer or backend invariance.

## Protocol Disclosure

| Instantiation | Dataset / split | Backend | Retrieval | Candidate budget | Seed(s) | Information access | Role |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| HumanEval+164 full fallback, Qwen | HumanEval+164 | Qwen-family main backend | fixed `syntax_aware` | 8 | 1 | code-aware diagnostic episodes | dataset boundary instantiation |
| HumanEval+50 DeepSeek slice | HumanEval+50 | DeepSeek supplementary backend | fixed `syntax_aware` | 8 | 1, 2 | code-aware diagnostic episodes | dataset + backend boundary instantiation |
| Granite 8B instruct/chat backend | MBPP+100 | local Granite 8B code instruct backend | fixed `syntax_aware` | 8 | 4 stochastic replicate labels | code-aware diagnostic episodes | non-Qwen/non-DeepSeek backend replicate boundary |
| StarCoder2-7B completion backend | MBPP+100 | local StarCoder2-7B completion backend | fixed `syntax_aware` | 8 | 4 stochastic replicate labels | code-aware diagnostic episodes | serving-format replicate boundary |
| Weak StarCoder-family MBPP+100 boundary | MBPP+100 | weak StarCoder-family backend | fixed `syntax_aware` | 8 | 1, 2 | code-aware diagnostic episodes | non-Qwen/non-DeepSeek backend boundary |

## Results

| Instantiation | Baseline | Prior setting | Baseline solved | Prior solved | Improved | Regressed | Unchanged | Interpretation |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| HumanEval+164 full fallback, Qwen | `no_prior + MBR` | `best_structure + MBR` | 138/164 | 138/164 | 3 | 3 | 158 | Full external non-degradation anchor; not a positive transfer claim. |
| HumanEval+50 DeepSeek slice | `no_prior + MBR` | `multi_prior + MBR` | 42/50 | 44/50 | 3 | 1 | 46 | Small slice-level positive audit instantiation on the supplementary backend. |
| HumanEval+50 DeepSeek slice, seed 2 | `no_prior + MBR` | `multi_prior + MBR` | 44/50 | 41/50 | 0 | 3 | 47 | Second seed reverses the seed-1 positive slice effect; mixed boundary evidence. |
| HumanEval+50 DeepSeek two-seed aggregate | `no_prior + MBR` | `multi_prior + MBR` | 86/100 | 85/100 | 3 | 4 | 93 | Aggregate is essentially neutral/slightly negative; not broad-transfer evidence. |
| StarCoder2-7B completion backend | `no_prior + MBR` | `multi_prior + MBR` | 74/100 | 72/100 | 4 | 6 | 90 | Completion-style non-Qwen/non-DeepSeek seed-1 boundary regresses under `multi_prior`. |
| StarCoder2-7B completion backend, seed 2 | `no_prior + MBR` | `multi_prior + MBR` | 72/100 | 75/100 | 5 | 2 | 93 | Second seed reverses seed 1; mixed backend evidence. |
| StarCoder2-7B completion two-seed aggregate | `no_prior + MBR` | `multi_prior + MBR` | 146/200 | 147/200 | 9 | 8 | 183 | Near-neutral mixed boundary evidence; useful for backend sensitivity, not invariance. |
| Granite 8B instruct/chat four-replicate aggregate | `no_prior + MBR` | `multi_prior + MBR` | 296/400 | 303/400 | 12 | 5 | 383 | Modest-positive but noisy instruct-backend boundary; candidate-pass delta is +47. |
| StarCoder2-7B completion four-replicate aggregate | `no_prior + MBR` | `multi_prior + MBR` | 282/400 | 300/400 | 29 | 11 | 360 | Positive after additional stochastic replicates, but still completion-style serving evidence. |
| Weak StarCoder-family MBPP+100 boundary | `no_prior + MBR` | `multi_prior + MBR` | 19/100 | 13/100 | 0 | 6 | 94 | Negative weak-backend boundary; supports backend sensitivity rather than invariance. |
| Weak StarCoder-family MBPP+100 boundary, seed 2 | `no_prior + MBR` | `multi_prior + MBR` | 14/100 | 8/100 | 1 | 7 | 92 | Second GPU seed again regresses under `multi_prior`. |
| Weak StarCoder-family MBPP+100 two-seed aggregate | `no_prior + MBR` | `multi_prior + MBR` | 33/200 | 21/200 | 1 | 13 | 186 | Repeated negative weak-backend evidence; reporting pattern applies, effect is backend-sensitive. |

## Raw Result Files

- `results/humanevalplus164_syntax_no_prior_mbrexec_budget8_seed1.json`
- `results/humanevalplus164_syntax_best_structure_budget8_seed1.json`
- `results/humanevalplus50_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed1.json`
- `results/humanevalplus50_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`
- `results/humanevalplus50_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed2.json`
- `results/humanevalplus50_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed2.json`
- `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed2.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed2.json`
- `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed2.json`
- `results/hf_safe_gpu_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json`
- `results/hf_safe_gpu_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`
- `results/hf_safe_gpu_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json`
- `results/hf_safe_gpu_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`

## Boundary

These rows use packaged outputs, including the newly added GPU seed-2 weak-backend, StarCoder2-7B, Granite, and DeepSeek HumanEval+50 runs. Positive, neutral, mixed, and negative rows are all retained. They instantiate the reporting pattern beyond the main MBPP table while preserving the claim boundary: these are not broad-transfer or backend-invariance evidence.
