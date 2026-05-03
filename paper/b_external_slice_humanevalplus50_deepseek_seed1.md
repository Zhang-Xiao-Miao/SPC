# External Slice

- Dataset: `humanevalplus50`
- Candidate Budget: `8`
- Seed: `1`
- Backend: `vllm_openai / deepseek-coder-6.7b-instruct`
- Note: this is a medium-size external slice on the currently active backend; it complements the full `HumanEval+164` fallback and the compatibility-filtered BigCodeBench-Hard modern slice.

| Setting | Pass Rate | Passed | Avg Latency | Avg Candidates |
| --- | ---: | ---: | ---: | ---: |
| no_prior | 0.8400 | 42/50 | 0.15 | 8.00 |
| multi_prior | 0.8800 | 44/50 | 0.27 | 8.00 |
