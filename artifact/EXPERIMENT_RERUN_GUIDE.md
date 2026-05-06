# Experiment Rerun Guide

This is a compact companion note. For the complete step-by-step path covering environment setup, dependencies, benchmark data reconstruction, model endpoint checks, smoke reruns, full MBPP+224 reruns, prompt-only reruns, and external/backend reruns, use `artifact/FULL_REPRODUCTION_GUIDE.md` first.

This artifact distinguishes three levels of reproduction. The first two are meant for every reviewer; the third is for reviewers who want to spend GPU/model time.

## Level 1: Numeric Claim Audit, No LLM

```bash
bash artifact/reviewer_audit.sh
```

Purpose: recompute headline paper quantities from packaged raw-result JSONs and prior-quality JSONs. This is the fastest way to check whether the manuscript numbers match the artifact.

Requires:

- Python
- packaged JSON result files
- no GPU
- no network
- no generated-code execution

## Level 2: Cached-Output Table Regeneration, No LLM

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

Purpose: regenerate paper-facing tables from cached outputs and verify provenance constraints.

This level does not regenerate raw model completions. It verifies that the paper-facing objects are derived from packaged cached outputs and that the matcher/prior-quality boundaries are inspectable.

## Level 3: Local Pipeline Smoke Test, Toy Data

```bash
bash artifact/run_smoke_test.sh
```

Purpose: run the real `plan_b.pipeline.run_pipeline` code path on a one-task synthetic fixture.

This uses `generator_backend=retrieval_edit`, so it does not call an LLM. It does execute generated toy Python code through the sandbox runner. It is a code-path smoke test, not paper evidence.

## Important Windows Smoke-Test Note

Python's `resource` module is Unix-only. The current artifact makes it optional in `rerank/sandbox_runner.py`: Linux/WSL/macOS use POSIX resource limits, while Windows smoke tests use subprocess timeout.

If `bash` is not available, run:

```bash
python scripts/71_run_pipeline_smoke_test.py
```

If you see `ModuleNotFoundError: No module named 'resource'`, you are using a stale artifact copy. That error is an environment-compatibility issue in the stale copy, not a paper-result failure.

## Level 4: Live Main-Experiment Rerun

Full live reruns require reconstructing benchmark assets under the expected `data/` layout and serving the matching model.

Expected data paths:

```text
data/processed/mbpp/train.jsonl
data/processed/evalplus/mbppplus_test.jsonl
data/episodes/mbppplus_test224_episodes.jsonl
```

Main experiment command shape:

```bash
python scripts/51_run_mbpp224_fair_budget.py \
  --dataset mbppplus224 \
  --retrieval syntax_aware \
  --settings no_prior,single_prior,multi_prior,random_prior,corrupted_prior \
  --budget 8 \
  --seeds 1,2,3 \
  --all-settings-use-all-seeds \
  --generator-backend vllm_openai \
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \
  --api-base http://127.0.0.1:8000/v1 \
  --device cuda \
  --out results/mbpp224_fair_budget/summary.json \
  --paper-out paper/b_mbpp224_fair_budget.md
```

Boundary: this command calls a live model and executes generated Python code. Run it only in an isolated environment with resource limits. Exact bit-for-bit equality is not guaranteed across model serving stacks, but the protocol, budgets, seeds, settings, and result paths are fixed.

## Level 5: Focused Live Reruns

For a cheaper live rerun, use a subset:

```bash
python scripts/51_run_mbpp224_fair_budget.py \
  --dataset mbppplus224 \
  --retrieval syntax_aware \
  --settings no_prior,multi_prior \
  --budget 8 \
  --seeds 1 \
  --max-episodes 20 \
  --generator-backend vllm_openai \
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \
  --api-base http://127.0.0.1:8000/v1 \
  --device cuda \
  --out results/live_rerun_smoke/summary.json \
  --paper-out paper/live_rerun_smoke.md
```

This does not reproduce the headline table, but it exercises the same live-inference path on a smaller slice.

## External And Backend Boundary Reruns

HumanEval+ / external slice shape:

```bash
python scripts/55_run_external_slice.py \
  --dataset humanevalplus50 \
  --settings no_prior,multi_prior \
  --candidate-budget 8 \
  --seed 1 \
  --generator-backend vllm_openai \
  --model-name deepseek-ai/deepseek-coder-6.7b-instruct \
  --api-base http://127.0.0.1:8001/v1
```

BigCodeBench-compatible reruns require reconstructing processed compatible slices; see `scripts/62_prepare_bigcodebench_slice.py`, `scripts/63_run_bigcodebench_slice.py`, and `artifact/SOURCE_AND_DATA.md`.

## Why The Direct Zip Does Not Include All Benchmark Data

The local benchmark-derived `data/` tree is multi-GB and includes upstream-derived tests/assets whose redistribution requires permission checks. The direct review zip therefore includes:

- complete project source code;
- cached raw-result JSONs supporting the paper claims;
- derived paper-facing tables;
- scripts to regenerate those tables;
- data layout and preparation notes for live reruns.

It does not include the multi-GB benchmark-derived data tree.
