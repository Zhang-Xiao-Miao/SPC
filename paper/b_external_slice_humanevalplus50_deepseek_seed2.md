# External Slice

- Dataset: `humanevalplus50`
- Candidate Budget: `8`
- Seed: `2`
- Note: using a local HumanEval+ slice fallback because newer external benchmarks are not available in the workspace.

| Setting | Pass Rate | Passed | Avg Latency | Avg Candidates |
| --- | ---: | ---: | ---: | ---: |
| no_prior | 0.8800 | 44/50 | 0.22 | 8.00 |
| multi_prior | 0.8200 | 41/50 | 0.37 | 8.00 |
