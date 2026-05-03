# Result Naming Rules

All new result paths should encode:

`<dataset>_<retrieval>_<setting>_<rerank>_budget<k>_seed<s>.json`

Additional backend-specific runs must also encode backend identity explicitly, for example:

`vllm_deepseek_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`

Rules:

1. Never write cross-model outputs to the canonical vLLM result names used by the main tables.
2. Keep benchmark, backend, budget, seed, and method visible in the filename.
3. If a script can target multiple backends, its default output path must remain backend-isolated.
4. Writing and artifact references should use the canonical `v2` paper objects; superseded paper objects remain in the repo only as historical drafts.
