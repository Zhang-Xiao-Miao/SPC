# Live Rerun Guide

Most reviewers should start with `artifact/REVIEWER_QUICKSTART.md`. This file is for users who want to rerun live LLM experiments after preparing external benchmark assets and model endpoints.

## Live Reruns Require

- upstream benchmark assets where redistribution is permitted;
- processed MBPP/EvalPlus/BigCodeBench-compatible files under the expected `data/` layout;
- model endpoints or local model weights;
- GPU/serving resources for larger models;
- matching tokenizer/backend versions;
- sandboxed execution for generated Python code;
- substantially more time than the reviewer quickstart.

## First Commands

```bash
cat artifact/FULL_REPRODUCTION_GUIDE.md
bash artifact/check_live_rerun_prereqs.sh
```

Items reported as live-rerun-only are not required for the default reviewer audit path.

## Live Rerun Verification Status

During the 2026-05-06 artifact preparation pass, a temporary local Qwen vLLM endpoint was started at `http://127.0.0.1:8000/v1` from the cached `Qwen/Qwen2.5-Coder-7B-Instruct` model. The full live LLM rerun was still not executed because that would require the complete multi-seed, full-task raw-completion regeneration and the additional boundary endpoints. The artifact therefore does not claim that a full raw-completion regeneration was completed.

The rerun path was still checked in the following ways:

- `artifact/check_live_rerun_prereqs.sh --check-endpoints` correctly reported Qwen main as reachable and missing boundary endpoints as optional live-only state;
- the documented driver scripts were checked for argument compatibility;
- a three-episode real-data MBPP+224 run was executed with the non-LLM `retrieval_edit` backend to validate data loading, episode loading, pipeline execution, sandboxed candidate execution, and output writing.
- a two-episode MBPP+224 live sanity run was executed against the real Qwen vLLM endpoint with `settings=no_prior,multi_prior`, `budget=1`, `seed=1`, and `max-episodes=2`; this validated endpoint integration, chat-completion generation, sandboxed evaluation, and result writing.

These smoke-scale checks are not paper evidence and are not substitutes for the full LLM rerun. The paper claims are verified from the packaged cached outputs by `artifact/reviewer_audit.sh`, `artifact/reproduce_main.sh`, and `artifact/verify_provenance.sh`.

## Main Rerun Shape

The main paper result is rerun with `scripts/51_run_mbpp224_fair_budget.py` after preparing `MBPP+224` episodes and starting a Qwen OpenAI-compatible endpoint at `http://127.0.0.1:8000/v1`. The full command is in `artifact/FULL_REPRODUCTION_GUIDE.md`.

## Important Boundary

Live reruns may not reproduce bit-identical raw completions because of model-serving nondeterminism. The canonical paper evidence is the packaged cached-output evidence listed in `artifact/CLAIM_TO_EVIDENCE.md`.

## Safety

Generated Python code is untrusted. Run live evaluation only in an isolated sandbox with resource limits and without sensitive credentials.

For live reruns that require third-party imports inside generated code, the sandbox runner can be configured with `PLANB_SANDBOX_DISABLE_SITE=0`. The default reviewer smoke test does not need this.
