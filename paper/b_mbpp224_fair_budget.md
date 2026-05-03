# MBPP+224 Fair-Budget Main Table

- Dataset: `mbppplus224`
- Retrieval: `syntax_aware`
- Candidate Budget: `8`
- Execution Budget: `8`
- Rerank: `mbr_exec`
- Source revision: `omitted_for_double_blind_review`

| Setting | Pass Rate Mean±Std | Solved Mean | Solved Range | Avg Latency | Avg Candidates | Prompt Tokens | Completion Tokens | Delta vs no_prior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_prior | 0.7976 ± 0.0026 | 178.67 | [178, 179] | 0.06 | 8.00 | 38261 | 14736 | +0.00 |
| single_prior | 0.8110 ± 0.0052 | 181.67 | [181, 183] | 0.05 | 8.00 | 46078 | 13182 | +3.00 |
| multi_prior | 0.8259 ± 0.0077 | 185.00 | [184, 187] | 0.10 | 8.00 | 46008 | 13195 | +6.33 |
| random_prior | 0.7693 ± 0.0026 | 172.33 | [172, 173] | 0.06 | 8.00 | 60193 | 13938 | -6.33 |
| corrupted_prior | 0.7738 ± 0.0068 | 173.33 | [172, 175] | 0.06 | 8.00 | 59927 | 13916 | -5.33 |
