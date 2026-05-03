# MBPP+100 Prompt-Only Lexical Fair-Budget Control

- Dataset: `mbppplus100`
- Retrieval: `lexical`
- Candidate Budget: `8`
- Execution Budget: `8`
- Rerank: `mbr_exec`
- Source revision: `omitted_for_double_blind_review`

This table is a prompt-only lexical retrieval control for the `syntax_aware` episode-construction risk. It is boundary evidence, not a positive transfer result.

| Setting | Pass Rate Mean+/-Std | Solved Mean | Solved Range | Avg Latency | Avg Candidates | Prompt Tokens | Completion Tokens | Delta vs no_prior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_prior | 0.8150 +/- 0.0071 | 81.50 | [81, 82] | 0.06 | 8.00 | 16447 | 6508 | +0.00 |
| single_prior | 0.8150 +/- 0.0071 | 81.50 | [81, 82] | 0.05 | 8.00 | 19882 | 5750 | +0.00 |
| multi_prior | 0.8050 +/- 0.0071 | 80.50 | [80, 81] | 0.10 | 8.00 | 19866 | 5781 | -1.00 |
