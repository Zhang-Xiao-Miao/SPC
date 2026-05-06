# Environment Notes

## Important Reviewer Note

The reviewer quickstart does not require GPU, model endpoints, API keys, network access, or generated-code execution. The GPU/model-serving details below document optional full live rerun conditions only.

## Recovered Software Snapshot

- Python: `Python 3.13.12`
- Python package snapshot recovered in the current shell:

```text
Name: vllm
Version: 0.11.2
Summary: A high-throughput and memory-efficient inference and serving engine for LLMs
Home-page: https://github.com/vllm-project/vllm
Author: vLLM Team
Author-email: 
License-Expression: Apache-2.0
Location: <CONDA_PREFIX>/lib/python3.13/site-packages
Requires: aiohttp, anthropic, blake3, cachetools, cbor2, cloudpickle, compressed-tensors, depyf, diskcache, einops, fastapi, filelock, flashinfer-python, gguf, lark, llguidance, lm-format-enforcer, mistral_common, model-hosting-container-standards, msgspec, ninja, numba, numpy, openai, openai-harmony, opencv-python-headless, outlines_core, partial-json-parser, pillow, prometheus-fastapi-instrumentator, prometheus_client, protobuf, psutil, py-cpuinfo, pybase64, pydantic, python-json-logger, pyyaml, pyzmq, ray, regex, requests, scipy, sentencepiece, setproctitle, setuptools, six, tiktoken, tokenizers, torch, torchaudio, torchvision, tqdm, transformers, typing_extensions, watchfiles, xformers, xgrammar
Required-by: 
---
Name: openai
Version: 2.30.0
Summary: The official Python library for the openai API
Home-page: https://github.com/openai/openai-python
Author: 
Author-email: OpenAI <support@openai.com>
License: Apache-2.0
Location: <CONDA_PREFIX>/lib/python3.13/site-packages
Requires: anyio, distro, httpx, jiter, pydantic, sniffio, tqdm, typing-extensions
Required-by: vllm
```

## Serving Backends Referenced By Results

- Primary historical Qwen runs: `generator_backend=vllm_openai`, `model_name=Qwen/Qwen2.5-Coder-7B-Instruct`, `api_base=http://127.0.0.1:8000/v1` as recorded in the raw result JSON config blocks.
- Added DeepSeek runs: `generator_backend=vllm_openai`, `model_name=deepseek-ai/deepseek-coder-6.7b-instruct`, `api_base=http://127.0.0.1:8001/v1` as recorded in `results/cross_model_deepseek_summary*.json` and raw DeepSeek result JSONs.
- Added Granite boundary runs: `generator_backend=vllm_openai`, `model_name=ibm-granite/granite-8b-code-instruct-4k`, `api_base=http://127.0.0.1:8003/v1`, served through chat.
- Added StarCoder2-7B boundary runs: `generator_backend=vllm_openai`, `model_name=bigcode/starcoder2-7b`, `api_base=http://127.0.0.1:8002/v1`, served through completions because the local tokenizer has no chat template.
- Current shell package check reports `vllm 0.11.2` and `openai 2.30.0`.
- The current shell does not report installed `evalplus` / `bigcodebench` packages, even though processed benchmark assets already exist in the repo. This implies the original preparation environment and the current packaging environment are not identical.

## Canonical Backend Identity For Writing

- Main-result backend for the paper: `Qwen/Qwen2.5-Coder-7B-Instruct`.
- Supplementary same-scale backend: `deepseek-ai/deepseek-coder-6.7b-instruct`.
- Granite 8B code instruct backend: `ibm-granite/granite-8b-code-instruct-4k`, used only as a replicate-sensitive instruction/chat boundary check.
- Completion-style StarCoder2-7B backend: `bigcode/starcoder2-7b`, used only as a serving-format boundary check.
- Weak backend: `bigcode-tiny-starcoder-py`, used only as a negative boundary check.

## Hardware Snapshot Recoverable At Packaging Time

```text
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              192
On-line CPU(s) list: 0-191
Thread(s) per core:  2
Core(s) per socket:  48
Socket(s):           2
NUMA node(s):        2
Vendor ID:           GenuineIntel
CPU family:          6
Model:               207
Model name:          INTEL(R) XEON(R) PLATINUM 8558P
Stepping:            2
CPU MHz:             3200.000
CPU max MHz:         4000.0000
CPU min MHz:         800.0000
BogoMIPS:            5400.00
Virtualization:      VT-x
L1d cache:           48K
L1i cache:           32K
L2 cache:            2048K
L3 cache:            266240K
NUMA node0 CPU(s):   0-47,96-143
NUMA node1 CPU(s):   48-95,144-191
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dtes64 ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb cat_l3 cat_l2 cdp_l3 invpcid_single cdp_l2 ssbd mba ibrs ibpb stibp ibrs_enhanced tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid cqm rdt_a avx512f avx512dq rdseed adx smap avx512ifma clflushopt clwb intel_pt avx512cd sha_ni avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local avx512_bf16 wbnoinvd dtherm ida arat pln pts hwp hwp_act_window hwp_epp hwp_pkg_req avx512vbmi umip pku ospke waitpkg avx512_vbmi2 gfni vaes vpclmulqdq avx512_vnni avx512_bitalg tme avx512_vpopcntdq la57 rdpid cldemote movdiri movdir64b enqcmd fsrm md_clear serialize tsxldtrk pconfig arch_lbr avx512_fp16 flush_l1d arch_capabilities
```

GPU query:

```text
NVIDIA H20-3e, 143771 MiB, 590.48.01
NVIDIA H20-3e, 143771 MiB, 590.48.01
NVIDIA H20-3e, 143771 MiB, 590.48.01
NVIDIA H20-3e, 143771 MiB, 590.48.01
NVIDIA H20-3e, 143771 MiB, 590.48.01
NVIDIA H20-3e, 143771 MiB, 590.48.01
NVIDIA H20-3e, 143771 MiB, 590.48.01
NVIDIA H20-3e, 143771 MiB, 590.48.01
```

## Boundary

- The repo now contains a packaging-time hardware snapshot, but not every original experiment wrote a machine-level hardware record into its raw result payload.
- The fair-budget claim should therefore be written from recorded candidate-budget and execution-call accounting, not from an unsupported claim of identical wall-clock or token-level compute.
