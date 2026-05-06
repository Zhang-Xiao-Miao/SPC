# Source And Data Inventory

## Executable Source Tree Included In Artifact

- `plan_b/`
- `generation/`
- `retrieval/`
- `structure/`
- `gating/`
- `rerank/`
- `guardrails/`
- `eval/`
- `verifier/`
- `scripts/`
- `configs/`

## Review Zip Data Strategy

The direct review zip excludes large upstream-derived benchmark data and tests so the package remains below the direct-upload size limit. The reviewer quickstart uses packaged cached outputs and raw-result JSONs; it does not need benchmark data, a GPU, a network connection, an API key, or live LLM calls.

Live reruns require reconstructing the expected `data/` layout from upstream benchmark sources and preparation scripts before invoking generation/evaluation commands. The canonical step-by-step procedure is `artifact/FULL_REPRODUCTION_GUIDE.md`; run `bash artifact/check_live_rerun_prereqs.sh` to see which data files, optional modules, and local endpoints are still missing in a fresh extracted copy.

## Expected Live-Rerun Data Layout

- `data/processed/mbpp/train.jsonl`
- `data/processed/evalplus/mbppplus_test.jsonl`
- `data/episodes/mbppplus_test224_episodes.jsonl`
- `data/episodes/mbppplus_test100_episodes.jsonl`
- `data/episodes/mbppplus_test100_prompt_structural_episodes.jsonl`
- `data/episodes/mbppplus_test224_prompt_structural_episodes.jsonl`
- `data/processed/evalplus/humanevalplus_test.jsonl`
- `data/episodes/humanevalplus_test164_syntax_episodes.jsonl`
- `data/episodes/humanevalplus_test50_syntax_episodes.jsonl`
- `data/processed/bigcodebench_hard_compatible30.jsonl`
- `data/processed/bigcodebench_hard_compatible50.jsonl`
- `data/episodes/bigcodebench_hard_compatible30_syntax_episodes.jsonl`
- `data/episodes/bigcodebench_hard_compatible50_syntax_episodes.jsonl`
- `data/processed/evalplus/tests/mbppplus/*.py`

## License And Redistribution Status

| Resource | Included in review artifact? | Public release status | License/permission status | Replacement if not redistributable |
| --- | --- | --- | --- | --- |
| MBPP processed examples | no, externalized from direct zip | release only if upstream terms permit | upstream benchmark-derived; permission must be verified before public redistribution | preparation script, expected layout, hashes, and cached outputs |
| EvalPlus MBPP+ tests | no, externalized from direct zip | release only if upstream terms permit | EvalPlus/benchmark-derived; permission must be verified before public redistribution | preparation script, expected layout, hashes, and cached outputs |
| HumanEval+ processed file | no, externalized from direct zip | release only if upstream terms permit | EvalPlus/HumanEval-derived; permission must be verified before public redistribution | preparation script, expected layout, hashes, and cached outputs |
| BigCodeBench-Hard compatible slices | no, externalized from direct zip | release only if upstream terms permit | BigCodeBench-derived; permission must be verified before public redistribution | compatibility-slice metadata, scripts, expected layout, hashes, and cached outputs |
| cached model outputs and derived paper tables | yes | releasable by authors subject to review policy | authors' generated outputs and derived summaries | N/A |

## Main Provenance Result Bundles Included In Artifact

- old uncontrolled comparison raw results for `paper/tbl_conclusion_shift.*`
- `results/mbppplus_vllm_v4_100_oracle.json`
- `results/mbppplus_vllm_v4_100_no_structure.json`
- `results/mbppplus_vllm_v4_100_random.json`
- `results/mbppplus_vllm_v4_100_corrupted.json`

These no-rerank files provide direct artifact-facing provenance for the `oracle > no_structure > corrupted/random` directionality claim and are summarized in `paper/tbl_no_rerank_directionality_v2.md`.

## External Evaluation Provenance

The package includes cached result JSONs and paper-facing summaries for HumanEval+, BigCodeBench-Hard compatible slices, Granite, StarCoder2, DeepSeek, and weak-backend boundary checks. The external benchmark inputs themselves are externalized from the direct zip and must be prepared from upstream sources for live reruns.

## Public Release Boundary

For public release, benchmark-derived files should be redistributed only after license/permission verification. If redistribution is not verified, release preparation scripts, metadata, expected layout, file hashes, cached output provenance, and instructions for users to obtain upstream assets themselves.
