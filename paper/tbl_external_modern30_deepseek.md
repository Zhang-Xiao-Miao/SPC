# Modern External Slice

- Dataset: `BigCodeBench-Hard v0.1.4` compatibility-filtered `30`-task slice
- Candidate Budget: `8`
- Seed: `1`
- Caveat: this slice is filtered for dependency compatibility with the current environment, so it supports a feasibility check rather than a full-benchmark generalization claim.

| Setting | Pass Rate | Passed | Avg Latency | Avg Candidates |
| --- | ---: | ---: | ---: | ---: |
| no_prior | 0.4667 | 14/30 | 0.18 | 8.00 |
| multi_prior | 0.3667 | 11/30 | 0.34 | 8.00 |
