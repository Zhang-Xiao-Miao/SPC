# MBPP+100 No-Rerank Directionality Provenance

- Dataset: `MBPP+100`
- Retrieval: `dense`
- Rerank: `none`
- Backend: `Qwen/Qwen2.5-Coder-7B-Instruct`
- Status: provenance table for mechanism support, not a headline benchmark.

| Setting | Prior Source | Solved | Pass Rate | Source File |
| --- | --- | ---: | ---: | --- |
| oracle_prior | query reference solution, diagnostic upper bound | 94/100 | 0.94 | `results/mbppplus_vllm_v4_100_oracle.json` |
| no_structure | no structural hint | 74/100 | 0.74 | `results/mbppplus_vllm_v4_100_no_structure.json` |
| corrupted_prior | corrupted oracle-derived diagnostic prior | 73/100 | 0.73 | `results/mbppplus_vllm_v4_100_corrupted.json` |
| random_prior | random training prior | 71/100 | 0.71 | `results/mbppplus_vllm_v4_100_random.json` |

Interpretation: without execution reranking, correct diagnostic structural information is clearly distinguishable from no structure and bad priors. This supports the proposal-quality mechanism, but the oracle and corrupted rows are diagnostic controls rather than deployable prior-construction methods.
