# Full Reproduction Guide

Most reviewers should not start here. Start with `artifact/REVIEWER_QUICKSTART.md` or the root `README.md`. This guide is for users who want to rerun live LLM generation after preparing upstream benchmark assets, model endpoints or local model weights, and sandboxed execution.

This is the single entry point for reviewers who want to move beyond cached-output audit and understand exactly what is needed to rerun the experiments. The guide is intentionally explicit about what is directly packaged, what must be downloaded or reconstructed, and which commands call live models.

## Reproduction Levels

| Level | Goal | Requires benchmark data? | Calls LLM? | Executes generated code? | Expected reviewer use |
| --- | --- | --- | --- | --- | --- |
| 0 | Understand project and claims | no | no | no | read `README.md`, `artifact/CLAIM_TO_EVIDENCE.md` |
| 1 | Verify paper numbers from packaged raw results | no | no | no | `bash artifact/reviewer_audit.sh` |
| 2 | Regenerate paper-facing tables from cached outputs | no | no | no | `bash artifact/reproduce_main.sh`; `bash artifact/verify_provenance.sh` |
| 3 | Run real code path on toy data | no | no | yes, toy code only | `bash artifact/run_smoke_test.sh` |
| 4 | Rerun live main experiment | yes | yes | yes | follow Sections 4-8 below |

Levels 1-3 are what every reviewer can run immediately after extracting the artifact. Level 4 is the full live rerun path and requires extra data/model setup.

## Important Windows Smoke-Test Note

Python's `resource` module is Unix-only. The current artifact makes it optional in `rerank/sandbox_runner.py`: Linux/WSL/macOS use POSIX resource limits, while Windows smoke tests use subprocess timeout.

On Windows without `bash`, run the Level 3 toy smoke test as:

```bash
python scripts/71_run_pipeline_smoke_test.py
```

If you see `ModuleNotFoundError: No module named 'resource'`, you are using a stale artifact copy. That error is an environment-compatibility issue in the stale copy, not a paper-result failure.

## 1. Create An Environment

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

For artifact review only, no third-party package is required beyond the packaged repository modules:

```bash
python -m pip install -r requirements-review.txt
```

For live reruns, install optional live dependencies:

```bash
python -m pip install -r requirements-live.txt
```

Notes:

- If you already have a managed OpenAI-compatible endpoint, you do not need to install `vllm` locally.
- If you serve models locally, install a `vllm`/`torch` stack matching your CUDA driver and hardware.
- Record your exact package versions if reporting live-rerun numbers, because serving stacks can affect stochastic generation.

## 2. Verify The Packaged Artifact Before Any Live Rerun

Run:

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

Expected headline output from `reviewer_audit.sh`:

```text
no_prior mean=178.67
multi_prior mean=185.00
pooled query-seed: improved=30, regressed=11, unchanged=631
task-clustered: positive=14, negative=5, zero=205
prompt-only multi_prior mean=177.67
code-aware multi_prior medium/high bins: coverage=0.469, improved=23, regressed=6, net=+17
[PASS] reviewer claim audit matched the paper's headline numbers and boundaries
```

This establishes that the paper-facing results in the artifact match the manuscript.

## 2.1 Current Live-Rerun Validation Status

The artifact preparation environment was used to start a temporary Qwen vLLM OpenAI-compatible endpoint at `http://127.0.0.1:8000/v1` from the cached `Qwen/Qwen2.5-Coder-7B-Instruct` model. Endpoint probing then reported Qwen main as reachable. The DeepSeek, StarCoder2, and Granite boundary endpoints at ports `8001`, `8002`, and `8003` were not running in that check.

What was actually validated:

- the optional prerequisite checker reports missing live assets/endpoints as optional live-only state, not default-review failure;
- documented command-line interfaces for the data-preparation and rerun scripts were checked against the scripts' `--help` output;
- a small MBPP+224 real-data rerun path was executed with the non-LLM `retrieval_edit` backend, validating data loading, episode loading, the PlanB pipeline, sandboxed candidate execution, and output writing.
- a two-episode MBPP+224 live sanity run was executed with the real Qwen vLLM endpoint:

```bash
python scripts/51_run_mbpp224_fair_budget.py \
  --dataset mbppplus224 \
  --retrieval syntax_aware \
  --settings no_prior,multi_prior \
  --budget 1 \
  --seeds 1 \
  --max-episodes 2 \
  --generator-backend vllm_openai \
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \
  --api-base http://127.0.0.1:8000/v1 \
  --device cpu \
  --out /tmp/planb_qwen_live_sanity/summary.json \
  --paper-out /tmp/planb_qwen_live_sanity/summary.md
```

Observed sanity output: both `no_prior` and `multi_prior` completed 2/2 tasks at `candidate_budget=1`, with nonzero prompt/completion token counts. These numbers are only a tiny endpoint-integration sanity check.

This validation supports the rerun instructions but does not claim that full raw LLM regeneration was completed. To run the full experiment, keep the required model endpoints running and then run the commands below.

## 3. Check Live-Rerun Prerequisites

Run:

```bash
bash artifact/check_live_rerun_prereqs.sh
```

To also probe local model endpoints:

```bash
bash artifact/check_live_rerun_prereqs.sh --check-endpoints
```

This script reports:

- whether default review files are present;
- which live-rerun-only data files are not yet prepared;
- which optional live-rerun Python modules are not yet installed;
- whether local `/v1/models` endpoints are reachable.

It exits successfully by default so reviewers can use it as a diagnostic report. Live-rerun-only items are not required for the default reviewer audit path. Use `--strict-live` if you want missing live-rerun prerequisites to fail the command.

## 4. Prepare Benchmark Data

The direct review zip does not include the multi-GB benchmark-derived `data/` tree. Reconstruct it under these paths.

### 4.1 MBPP

Install `datasets`, then run:

```bash
python scripts/00_prepare_mbpp.py --output-dir data/processed/mbpp
```

Expected outputs:

```text
data/processed/mbpp/train.jsonl
data/processed/mbpp/test.jsonl
data/processed/mbpp/tests/train/*.py
data/processed/mbpp/tests/test/*.py
```

### 4.2 EvalPlus MBPP+ And HumanEval+

Place upstream EvalPlus raw files here:

```text
data/raw/evalplus/MbppPlus.jsonl.gz
data/raw/evalplus/HumanEvalPlus.jsonl.gz
```

Then run:

```bash
python scripts/03_prepare_evalplus.py \
  --mbppplus-path data/raw/evalplus/MbppPlus.jsonl.gz \
  --humanevalplus-path data/raw/evalplus/HumanEvalPlus.jsonl.gz \
  --output-dir data/processed/evalplus
```

Expected outputs:

```text
data/processed/evalplus/mbppplus_test.jsonl
data/processed/evalplus/humanevalplus_test.jsonl
data/processed/evalplus/tests/mbppplus/*.py
data/processed/evalplus/tests/humanevalplus/*.py
```

### 4.3 Build Main Episodes

Main code-aware `syntax_aware` episodes:

```bash
mkdir -p data/episodes
python scripts/01_build_episodes.py \
  --train-path data/processed/mbpp/train.jsonl \
  --eval-path data/processed/evalplus/mbppplus_test.jsonl \
  --output-path data/episodes/mbppplus_test224_episodes.jsonl \
  --shots 1 \
  --retrieval-modes syntax_aware \
  --limit-eval 224
```

Prompt-only structural boundary episodes:

```bash
python scripts/01_build_episodes.py \
  --train-path data/processed/mbpp/train.jsonl \
  --eval-path data/processed/evalplus/mbppplus_test.jsonl \
  --output-path data/episodes/mbppplus_test224_prompt_structural_episodes.jsonl \
  --shots 1 \
  --retrieval-modes prompt_structural \
  --limit-eval 224
```

MBPP+100 support episodes for boundary checks:

```bash
python scripts/01_build_episodes.py \
  --train-path data/processed/mbpp/train.jsonl \
  --eval-path data/processed/evalplus/mbppplus_test.jsonl \
  --output-path data/episodes/mbppplus_test100_episodes.jsonl \
  --shots 1 \
  --retrieval-modes syntax_aware \
  --limit-eval 100
```

HumanEval+50 syntax episodes:

```bash
python scripts/01_build_episodes.py \
  --train-path data/processed/mbpp/train.jsonl \
  --eval-path data/processed/evalplus/humanevalplus_test.jsonl \
  --output-path data/episodes/humanevalplus_test50_syntax_episodes.jsonl \
  --shots 1 \
  --retrieval-modes syntax_aware \
  --limit-eval 50
```

### 4.4 BigCodeBench-Hard Compatible Slices

BigCodeBench-Hard requires a local upstream Arrow export or dataset cache. Set:

```bash
export BIGCODEBENCH_HARD_ARROW=data/upstream/bigcodebench-hard-v0.1.4.arrow
```

Then prepare a compatibility-filtered slice:

```bash
python scripts/62_prepare_bigcodebench_slice.py \
  --max-tasks 50 \
  --source-arrow "$BIGCODEBENCH_HARD_ARROW" \
  --out-examples data/processed/bigcodebench_hard_compatible50.jsonl \
  --out-episodes data/episodes/bigcodebench_hard_compatible50_syntax_episodes.jsonl \
  --paper-out paper/tbl_external_modern_sampling50.md
```

Boundary: this is a compatibility-filtered slice, not a random sample of the full benchmark.

## 5. Start Model Endpoints

The main paper result uses an OpenAI-compatible endpoint for `Qwen/Qwen2.5-Coder-7B-Instruct` at:

```text
http://127.0.0.1:8000/v1
```

Typical local vLLM command shape:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --served-model-name Qwen/Qwen2.5-Coder-7B-Instruct \
  --host 127.0.0.1 \
  --port 8000
```

Supplementary endpoints used by boundary checks:

```text
DeepSeek:    http://127.0.0.1:8001/v1   deepseek-ai/deepseek-coder-6.7b-instruct
StarCoder2:  http://127.0.0.1:8002/v1   bigcode/starcoder2-7b
Granite:     http://127.0.0.1:8003/v1   ibm-granite/granite-8b-code-instruct-4k
```

Check endpoint readiness:

```bash
bash artifact/check_live_rerun_prereqs.sh --check-endpoints
```

## 6. Run A Small Live Smoke Rerun

Before running the full table, run a small live slice into a separate output directory:

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

This confirms that data loading, retrieval, live generation, and `MBR-exec` execution are working. It is not the paper headline result.

## 7. Run The Full MBPP+224 Main Table

Use a separate output directory first, so the packaged audit files remain intact:

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
  --out results/live_mbpp224_fair_budget/summary.json \
  --paper-out paper/live_mbpp224_fair_budget.md
```

Expected shape:

- five settings: `no_prior`, `single_prior`, `multi_prior`, `random_prior`, `corrupted_prior`;
- seeds `1,2,3` for all settings;
- candidate budget `8`;
- execution budget `8`;
- output raw JSONs under `results/live_mbpp224_fair_budget/`;
- summary table at `paper/live_mbpp224_fair_budget.md`.

Because live model serving is stochastic and backend implementations can differ, this guide does not promise bit-for-bit equality. The paper artifact preserves the original cached raw outputs and verifies the exact reported numbers. A live rerun should be interpreted as protocol reproduction under the same settings.

## 8. Recompute Paper Tables From A Completed Full Rerun

The canonical reviewer audit reads the packaged canonical paths. To regenerate the paper-facing objects from the packaged canonical cached outputs, run:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

If you intentionally overwrite the canonical `results/mbpp224_fair_budget/summary.json` with your live rerun, then rerun:

```bash
python scripts/58_make_stats_and_cost.py
python scripts/67_make_prior_quality_audit.py
python scripts/68_make_prior_quality_response.py
```

Do this only in a copied workspace if you want to preserve the original artifact evidence.

## 9. Rerun Prompt-Only Boundary Controls

Prompt-only structural reruns use the prompt-structural episode file:

```bash
python scripts/51_run_mbpp224_fair_budget.py \
  --dataset mbppplus224 \
  --retrieval prompt_structural \
  --settings no_prior,single_prior,multi_prior \
  --budget 8 \
  --seeds 1,2,3 \
  --episodes-path data/episodes/mbppplus_test224_prompt_structural_episodes.jsonl \
  --generator-backend vllm_openai \
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \
  --api-base http://127.0.0.1:8000/v1 \
  --device cuda \
  --out results/live_prompt_only_structural_mbpp224/summary.json \
  --paper-out paper/live_prompt_only_structural_mbpp224.md
```

This is the live counterpart of the full prompt-only boundary result in the paper.

## 10. Rerun External / Backend Boundary Checks

HumanEval+50 DeepSeek shape:

```bash
python scripts/55_run_external_slice.py \
  --dataset humanevalplus50 \
  --settings no_prior,multi_prior \
  --candidate-budget 8 \
  --seed 1 \
  --generator-backend vllm_openai \
  --model-name deepseek-ai/deepseek-coder-6.7b-instruct \
  --api-base http://127.0.0.1:8001/v1 \
  --result-prefix live_humanevalplus50_deepseek \
  --out results/live_external_slice_humanevalplus50_deepseek_seed1.json \
  --paper-out paper/live_external_slice_humanevalplus50_deepseek_seed1.md
```

BigCodeBench-Hard compatible slice shape:

```bash
python scripts/63_run_bigcodebench_slice.py \
  --settings no_prior,multi_prior \
  --candidate-budget 8 \
  --seed 1 \
  --generator-backend vllm_openai \
  --model-name deepseek-ai/deepseek-coder-6.7b-instruct \
  --api-base http://127.0.0.1:8001/v1 \
  --eval-examples data/processed/bigcodebench_hard_compatible50.jsonl \
  --episodes data/episodes/bigcodebench_hard_compatible50_syntax_episodes.jsonl \
  --slice-tag bigcodebench_hard_compatible50 \
  --max-episodes 50 \
  --result-prefix live_bigcodebench_hard_compatible50 \
  --out results/live_external_slice_bigcodebench_hard50_seed1.json \
  --paper-out paper/live_external_slice_bigcodebench_hard50_seed1.md
```

Refer to `artifact/PAPER_TO_ARTIFACT_MAP.md` for the packaged cached outputs corresponding to boundary rows.

## 11. Safety

Live reruns execute generated Python code. Run them only in a sandboxed environment with:

- no sensitive credentials;
- no unnecessary network access;
- resource limits;
- disposable working directories;
- monitoring for timeouts and runaway processes.

The default reviewer audit does not execute generated code.

For full live reruns that execute untrusted generated programs, a Linux/WSL/container environment is preferred because POSIX resource limits and process isolation are easier to enforce there. The toy smoke test itself is cross-platform.

## 12. Troubleshooting

- Missing `data/processed/mbpp/train.jsonl`: run `scripts/00_prepare_mbpp.py`.
- Missing `data/raw/evalplus/*.jsonl.gz`: obtain upstream EvalPlus raw files and place them under `data/raw/evalplus/`.
- Missing `data/episodes/*.jsonl`: run the episode-building commands in Section 4.3.
- Endpoint not reachable: start vLLM/OpenAI-compatible server and rerun `bash artifact/check_live_rerun_prereqs.sh --check-endpoints`.
- `ModuleNotFoundError` for live reruns: install `requirements-live.txt`.
- Different live numbers: check model identity, serving mode, temperature, candidate budget, seeds, endpoint implementation, and whether outputs were written to a separate directory or overwrote canonical cached results.
