# MBPP+100 Prompt-Only Structural Fair-Budget Control

- Dataset: `mbppplus100`
- Retrieval: `prompt_structural`
- Candidate Budget: `8`
- Execution Budget: `8`
- Rerank: `mbr_exec`
- Source revision: `omitted_for_double_blind_review`

This table reports a pre-specified prompt-only structural retrieval control. Query-side retrieval uses the task prompt and entry point only; support-side matching may use support code from the training pool. It is a narrow control, not a new prior-construction method.

Paired query-seed changes against `no_prior`: `single_prior` has 4 improvements, 7 regressions, and 189 unchanged cases; `multi_prior` has 5 improvements, 3 regressions, and 192 unchanged cases.

| Setting | Pass Rate Mean+/-Std | Solved Mean | Solved Range | Avg Latency | Avg Candidates | Prompt Tokens | Completion Tokens | Delta vs no_prior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_prior | 0.8250 +/- 0.0212 | 82.50 | [81, 84] | 0.07 | 8.00 | 16166 | 6686 | +0.00 |
| single_prior | 0.8100 +/- 0.0000 | 81.00 | [81, 81] | 0.05 | 8.00 | 19299 | 5796 | -1.50 |
| multi_prior | 0.8350 +/- 0.0071 | 83.50 | [83, 84] | 0.10 | 8.00 | 19278 | 5757 | +1.00 |
