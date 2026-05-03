# Data Release Policy

This anonymous review artifact is packaged for NeurIPS review. It is not a public benchmark redistribution.

## Review Package Policy

- Large upstream-derived benchmark data and tests are externalized from the direct review zip to keep the package below the direct-upload size limit.
- The reviewer quickstart uses packaged cached outputs and raw-result JSONs only.
- The quickstart does not require network access, GPU access, API keys, live LLM endpoints, or execution of generated code.
- Live reruns require reconstructing the expected `data/` layout from upstream sources and then using the packaged source and scripts.

## Redistribution Status

| Resource | Included in review artifact? | Public release status | License/permission status | Replacement if not redistributable |
| --- | --- | --- | --- | --- |
| MBPP processed examples | no, externalized from direct zip | release only if upstream terms permit | upstream benchmark-derived; permission must be verified before public redistribution | preparation script + hashes + expected layout |
| EvalPlus MBPP+ tests | no, externalized from direct zip | release only if upstream terms permit | EvalPlus/benchmark-derived; permission must be verified before public redistribution | preparation script + hashes + expected layout |
| HumanEval+ processed file | no, externalized from direct zip | release only if upstream terms permit | EvalPlus/HumanEval-derived; permission must be verified before public redistribution | preparation script + hashes + expected layout |
| BigCodeBench-Hard compatible slices | no, externalized from direct zip | release only if upstream terms permit | BigCodeBench-derived; permission must be verified before public redistribution | compatibility metadata + scripts + hashes |
| cached model outputs | yes | releasable by authors subject to review/public-release policy | authors' generated outputs | N/A |

## Public Release Plan

For the camera-ready public release, add a final project license and only include upstream-derived benchmark files when redistribution permission is verified. Otherwise, publish preparation scripts, metadata, expected directory layout, hashes, and cached-output provenance rather than restricted upstream data.
