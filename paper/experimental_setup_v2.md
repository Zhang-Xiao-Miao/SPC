# Experimental Setup V2

## Canonical Backend Identity

- Main-result backend: `vllm_openai / Qwen2.5-Coder-7B-Instruct`
- Main-result endpoint recorded in raw result configs: `http://127.0.0.1:8000/v1`
- Supplementary same-scale backend: `vllm_openai / deepseek-ai/deepseek-coder-6.7b-instruct`
- Supplementary endpoint recorded in added runs: `http://127.0.0.1:8001/v1`
- Supplemental Granite boundary backend: `vllm_openai chat / ibm-granite/granite-8b-code-instruct-4k`
- Local completion-style boundary backend: `vllm_openai completions / bigcode/starcoder2-7b`
- Local StarCoder2 endpoint used for the added run: `http://127.0.0.1:8002/v1`
- Weak boundary-check backend: `hf_causal / bigcode-tiny-starcoder-py`

Interpretation rule:

- All primary `MBPP+224` fair-budget conclusions are anchored on the Qwen backend.
- DeepSeek is supplementary cross-model and external-support evidence.
- Granite is a supplemental instruction/chat backend boundary check; its four-replicate aggregate is modest-positive but noisy.
- StarCoder2-7B is a completion-style boundary check; its four-replicate aggregate is positive but should not be written as clean instruction-backend evidence.
- The weak backend is a boundary check only and must not be written as symmetric evidence against the main backend.

## Main Benchmark Protocol

- Dataset: `MBPP+224`
- Retrieval: `syntax_aware`
- Candidate budget: `8`
- Rerank: `MBR-exec`
- Fairness definition: matched candidate budget plus matched execution-call accounting
- Non-claim: prompt-token totals are not equal across prior conditions, so this is not full compute equality
- Information-access status: `syntax_aware` episode construction uses stored code fields and is therefore fixed code-aware diagnostic evidence, not deployable prompt-only retrieval
- Rerank status: `MBR-exec` uses task tests for candidate selection and solved-count reporting, so it is diagnostic execution-selection rather than a deployment-time selection method. In the direct review zip, large upstream-derived benchmark tests are externalized; cached outputs remain packaged for reviewer quickstart.

## Prompt-Only Structural Control

- Implementation: `retrieval/prompt_structural.py`
- Specification: `paper/prompt_only_structural_matcher.md`
- Query-side access: task prompt text and entry point only
- Support-side access: training-pool prompt, entry point, and support-code structure
- Fixed score: `0.45 * lexical_cosine + 0.20 * prompt_intent_jaccard + 0.35 * structural_tag_jaccard`
- Provenance: the formula and constants in `retrieval/prompt_structural.py` are the fixed matcher used for both prompt-only structural controls; the reported full `MBPP+224` rerun is not selected from an alternative-weight sweep, and no alternative-weight sweep is used in the canonical artifact
- Non-claim: this is a boundary control, not a new prior-construction method

## Seed Policy

- Main fair-budget table:
  `no_prior`, `single_prior`, `multi_prior` use seeds `1,2,3`
- Bad-prior rows:
  `random_prior`, `corrupted_prior` now use seeds `1,2,3`
- Budget sweep:
  budgets `1,4,8,16` currently use seeds `1,2`
- Cross-model:
  Qwen uses seeds `1,2`; DeepSeek uses seeds `1,2`; StarCoder2-7B uses seeds `1,2`; weak backend uses GPU seeds `1,2`
- Backend replicate boundary checks:
  Granite and StarCoder2 use four stochastic replicate labels on `MBPP+100`; the pipeline seed is not passed into the vLLM OpenAI payload, so these labels are not deterministic generation seeds

## External Protocol Identity

- `HumanEval+164`: full external fallback, rerunnable after reconstructing upstream-derived inputs
- `HumanEval+50`: medium-size external slice, mixed across two DeepSeek seeds
- `BigCodeBench-Hard compatible30/50`: compatibility-filtered modern slices, rerunnable after reconstructing processed inputs from upstream sources

Writing rule:

- external evidence is qualified and slice-sensitive
- cross-model evidence is backend-sensitive and qualified
- bad-prior decomposition beyond the aggregate delta is now backed by seeds `1,2,3`, with `all_compile_fail` remaining dominant and small timeout spillover appearing in `corrupted_prior`
- prompt-only controls bound the main claim; the full `MBPP+224` prompt-only structural rerun is non-positive
- prior-quality audit is retrospective and reference-code-based; it is consistent with the boundary but does not solve prior construction
- reviewer-facing table scripts regenerate paper objects from cached outputs and raw-result JSONs; full LLM reruns require reconstructed benchmark inputs plus a matching model endpoint or local model
- use `paper/audit_reporting_checklist.md` and `artifact/CLAIM_SURVIVAL_CARD.md` as the reusable E&D reporting objects when writing the final manuscript
