# Bad Prior Failure Breakdown

This breakdown upgrades the claim `bad priors remain harmful` from a single solved-task delta into a per-query regression summary on the main `MBPP+224 fair-budget` benchmark. The goal is to clarify whether the remaining harm is compile-related, rerank-related, or timeout-related.
This revision uses seed-complete comparisons for seeds `1,2,3` whenever the packaged canonical result files are available.

## random_prior

### seed 1

Relative to `no_prior + MBR`, this setting gained `9` tasks and regressed `15` tasks under the same budget and rerank regime.
- `mbppplus_67`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_108`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_145`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_233`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_245`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_259`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_264`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_282`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_283`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_285`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`

### seed 2

Relative to `no_prior + MBR`, this setting gained `8` tasks and regressed `15` tasks under the same budget and rerank regime.
- `mbppplus_57`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_61`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_67`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_79`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_101`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_123`: `other_execution_failure`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_142`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_145`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_239`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_252`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`

### seed 3

Relative to `no_prior + MBR`, this setting gained `8` tasks and regressed `14` tasks under the same budget and rerank regime.
- `mbppplus_62`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_101`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_106`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_140`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_145`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_239`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_245`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_256`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_285`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`
- `mbppplus_410`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`random_1`

## corrupted_prior

### seed 1

Relative to `no_prior + MBR`, this setting gained `10` tasks and regressed `17` tasks under the same budget and rerank regime.
- `mbppplus_61`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_67`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_108`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_145`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_233`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_245`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_264`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_280`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_283`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_285`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`

### seed 2

Relative to `no_prior + MBR`, this setting gained `12` tasks and regressed `16` tasks under the same budget and rerank regime.
- `mbppplus_61`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_67`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_79`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_101`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_106`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_123`: `best_timeout`, target exec=`timeout`, target compile_ok=`True`, candidate priors=`corrupted`
- `mbppplus_245`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_252`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_292`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_388`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`

### seed 3

Relative to `no_prior + MBR`, this setting gained `12` tasks and regressed `17` tasks under the same budget and rerank regime.
- `mbppplus_62`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_90`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_145`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_224`: `best_timeout`, target exec=`timeout`, target compile_ok=`True`, candidate priors=`corrupted`
- `mbppplus_239`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_256`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_259`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_285`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_292`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
- `mbppplus_410`: `all_compile_fail`, target exec=`failed`, target compile_ok=`False`, candidate priors=`corrupted`
