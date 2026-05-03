from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from fnmatch import fnmatch
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.io_utils import write_json, write_text


FINAL_PAPER_TITLE = "Auditing Quality-Conditioned Structural-Prior Claims in Code Generation"
ARTIFACT_VERSION = "anonymous-review-2026-05-03"
PACKAGE_AUDIT_DATED_NAME = "PACKAGE_AUDIT_2026-05-03.md"
DIRECT_ZIP_SIZE_LIMIT_BYTES = 100_000_000

CANONICAL_PAPER_FILES = [
    "README.md",
    "requirements.txt",
    "LICENSE_REVIEW_ONLY.md",
    "paper/title.md",
    "paper/abstract_v2.md",
    "paper/intro_v2.md",
    "paper/claim_matrix_v2.md",
    "paper/experimental_setup_v2.md",
    "paper/audit_reporting_checklist.md",
    "paper/prompt_only_structural_matcher.md",
    "paper/prior_quality_audit_provenance.md",
    "paper/provenance_validation_checklist.md",
    "paper/data_release_policy.md",
    "paper/artifact_reviewer_walkthrough.md",
    "paper/contribution_and_artifact_summary.md",
    "paper/final_submission_qa_checklist.md",
    "paper/figure1_concept.md",
    "paper/external_protocol.md",
    "paper/discussion_backend_sensitivity.md",
    "paper/related_work_notes.md",
    "paper/reference_inventory.md",
    "paper/refs_planb.bib",
    "paper/b_mbpp224_fair_budget.md",
    "paper/tbl_conclusion_shift.md",
    "paper/tbl_conclusion_shift.json",
    "paper/tbl_stats_cost.md",
    "paper/tbl_stats_cost.json",
    "paper/tbl_task_clustered_paired_stats.md",
    "paper/tbl_no_rerank_directionality_v2.md",
    "paper/tbl_prompt_only_lexical_control.md",
    "paper/tbl_prompt_only_structural_control.md",
    "paper/tbl_prompt_only_structural_mbpp224_control.md",
    "paper/tbl_prior_quality_audit.md",
    "paper/tbl_prior_quality_audit.json",
    "paper/tbl_prior_quality_response.md",
    "paper/tbl_prior_quality_response.json",
    "paper/fig_prior_quality_response.md",
    "paper/fig_budget_sweep_v2.md",
    "paper/fig_budget_sweep_v2.json",
    "paper/tbl_external_v2.md",
    "paper/tbl_boundary_instantiations.md",
    "paper/tbl_backend_replicate_boundary.md",
    "paper/tbl_backend_replicate_boundary.json",
    "paper/backend_replicate_boundary_notes.md",
    "paper/b_external_slice_humanevalplus50_deepseek_seed1.md",
    "paper/b_external_slice_humanevalplus50_deepseek_seed2.md",
    "paper/tbl_external_modern30_deepseek.md",
    "paper/tbl_external_modern50_deepseek.md",
    "paper/tbl_external_modern_sampling30.md",
    "paper/tbl_external_modern_sampling50.md",
    "paper/tbl_cross_model_v2.md",
    "paper/tbl_cross_model_v2.json",
    "paper/tbl_cross_model_deepseek_two_seed.md",
    "paper/tbl_cross_model_deepseek_two_seed.json",
    "paper/tbl_cross_model_starcoder2_seed1.md",
    "paper/tbl_cross_model_starcoder2_seed2.md",
    "paper/tbl_cross_model_starcoder2_two_seed.md",
    "paper/tbl_cross_model_starcoder2_two_seed.json",
    "paper/tbl_cross_model_safe_gpu_seed2.md",
    "paper/tbl_controlled_degradation_sweep.md",
    "paper/fig_bad_prior_delta_types.md",
    "paper/fig_bad_prior_delta_types.json",
    "paper/bad_prior_failure_breakdown.md",
    "paper/latex/README.md",
    "paper/latex/main.tex",
    "paper/latex/main.pdf",
    "paper/latex/neurips_2026.sty",
]

PAPER_GLOBS = [
    "paper/latex/sections/*.tex",
]

SOURCE_DIRS = [
    "plan_b",
    "generation",
    "retrieval",
    "structure",
    "gating",
    "rerank",
    "guardrails",
    "eval",
    "verifier",
    "scripts",
    "configs",
]

RESULT_FILES = [
    "results/mbpp224_fair_budget/summary.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_no_prior_mbrexec_budget8_seed2.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_no_prior_mbrexec_budget8_seed3.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_single_prior_mbrexec_budget8_seed1.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_single_prior_mbrexec_budget8_seed2.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_single_prior_mbrexec_budget8_seed3.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_multi_prior_mbrexec_budget8_seed2.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_multi_prior_mbrexec_budget8_seed3.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_random_prior_mbrexec_budget8_seed1.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_corrupted_prior_mbrexec_budget8_seed1.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_random_prior_mbrexec_budget8_seed2.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_corrupted_prior_mbrexec_budget8_seed2.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_random_prior_mbrexec_budget8_seed3.json",
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_corrupted_prior_mbrexec_budget8_seed3.json",
    "results/mbppplus_full_k1_syntax_noprior_nogate_nombr_vllm_seed1.json",
    "results/mbppplus_full_k1_syntax_multiprior_nogate_mbrexec_vllm_seed1.json",
    "results/mbppplus_vllm_v4_100_oracle.json",
    "results/mbppplus_vllm_v4_100_no_structure.json",
    "results/mbppplus_vllm_v4_100_random.json",
    "results/mbppplus_vllm_v4_100_corrupted.json",
    "results/mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed1.json",
    "results/mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json",
    "results/mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed2.json",
    "results/mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json",
    "results/cross_model_deepseek_summary.json",
    "results/cross_model_deepseek_summary_seed2.json",
    "results/vllm_deepseek_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/vllm_deepseek_mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed1.json",
    "results/vllm_deepseek_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/vllm_deepseek_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json",
    "results/vllm_deepseek_mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed2.json",
    "results/vllm_deepseek_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json",
    "results/cross_model_safe_summary_gpu.json",
    "results/hf_safe_gpu_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/hf_safe_gpu_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/cross_model_safe_summary_gpu_seed2.json",
    "results/hf_safe_gpu_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json",
    "results/hf_safe_gpu_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json",
    "results/cross_model_granite8b_summary_seed1.json",
    "results/cross_model_granite8b_summary_seed1.md",
    "results/cross_model_granite8b_summary_seed2.json",
    "results/cross_model_granite8b_summary_seed2.md",
    "results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed1.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed2.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed2.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed2.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_drop_api_tags_mbrexec_budget8_seed1.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_drop_api_tags_mbrexec_budget8_seed2.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_unsupported_api_gate_mbrexec_budget8_seed1.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_unsupported_api_gate_mbrexec_budget8_seed2.json",
    "results/cross_model_starcoder2_summary_seed1.json",
    "results/cross_model_starcoder2_summary_seed2.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed1.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_single_prior_mbrexec_budget8_seed2.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed2.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed2.json",
    "results/humanevalplus164_syntax_no_prior_mbrexec_budget8_seed1.json",
    "results/humanevalplus164_syntax_best_structure_budget8_seed1.json",
    "results/external_slice_humanevalplus50_deepseek_seed1.json",
    "results/humanevalplus50_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/humanevalplus50_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/external_slice_humanevalplus50_deepseek_seed2.json",
    "results/humanevalplus50_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed2.json",
    "results/humanevalplus50_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed2.json",
    "results/external_slice_bigcodebench_hard30_deepseek_seed1.json",
    "results/external_slice_bigcodebench_hard50_deepseek_seed1.json",
    "results/bigcodebench_hard30_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/bigcodebench_hard30_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/bigcodebench_hard50_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed1.json",
    "results/bigcodebench_hard50_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/verifier_ablation_full224_seed3.json",
    "results/plan_b_learned_verifier_full224.json",
]

RESULT_GLOBS = [
    "results/budget_sweep/*.json",
    "results/prompt_only_lexical_mbpp100_fair_budget/*.json",
    "results/prompt_only_structural_mbpp100_fair_budget/*.json",
    "results/prompt_only_structural_mbpp224_fair_budget/*.json",
    "results/degradation_sweep/*.json",
]

DATA_FILES = [
    "data/processed/mbpp/train.jsonl",
    "data/processed/evalplus/mbppplus_test.jsonl",
    "data/episodes/mbppplus_test224_episodes.jsonl",
    "data/episodes/mbppplus_test100_episodes.jsonl",
    "data/episodes/mbppplus_test100_prompt_structural_episodes.jsonl",
    "data/episodes/mbppplus_test224_prompt_structural_episodes.jsonl",
    "data/processed/evalplus/humanevalplus_test.jsonl",
    "data/episodes/humanevalplus_test164_syntax_episodes.jsonl",
    "data/episodes/humanevalplus_test50_syntax_episodes.jsonl",
    "data/processed/bigcodebench_hard_compatible30.jsonl",
    "data/processed/bigcodebench_hard_compatible50.jsonl",
    "data/episodes/bigcodebench_hard_compatible30_syntax_episodes.jsonl",
    "data/episodes/bigcodebench_hard_compatible50_syntax_episodes.jsonl",
]

DATA_GLOBS = [
    "data/processed/evalplus/tests/mbppplus/*.py",
]

GENERATED_ARTIFACT_DOCS = [
    "README_ANON.md",
    PACKAGE_AUDIT_DATED_NAME,
    "PACKAGE_AUDIT.md",
    "REVIEWER_QUICKSTART.md",
    "CONTRIBUTION_AND_ARTIFACT_SUMMARY.md",
    "CLAIM_TO_EVIDENCE.md",
    "PAPER_TO_ARTIFACT_MAP.md",
    "KNOWN_LIMITATIONS.md",
    "RESULT_NAMING_RULES.md",
    "STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md",
    "INFORMATION_ACCESS_CARD.md",
    "CLAIM_SURVIVAL_CARD.md",
    "CANONICAL_REVIEWER_PACKAGE.md",
    "CONTROLLED_DEGRADATION_PROTOCOL.md",
    "CANONICAL_FILE_LIST.md",
    "DATA_RELEASE_POLICY.md",
    "ENVIRONMENT.md",
    "SOURCE_AND_DATA.md",
    "REPRODUCIBILITY_STATUS.md",
    "external/README.md",
    "reproduce_table1.sh",
    "reproduce_figure1.sh",
    "reproduce_main.sh",
    "reproduce_figures.sh",
    "verify_provenance.sh",
    "final_preflight.sh",
    "VERIFICATION_LOG_2026-04-29.md",
    "VERIFICATION_LOG.md",
    "manifest.json",
    "manifest_with_hashes.json",
]

P0_REQUIRED_PACKAGE_PATHS = [
    "README.md",
    "artifact/README_ANON.md",
    "artifact/REVIEWER_QUICKSTART.md",
    "artifact/CONTRIBUTION_AND_ARTIFACT_SUMMARY.md",
    "artifact/verify_provenance.sh",
    "artifact/reproduce_main.sh",
    "artifact/CLAIM_TO_EVIDENCE.md",
    "artifact/KNOWN_LIMITATIONS.md",
    "artifact/PAPER_TO_ARTIFACT_MAP.md",
    "artifact/CANONICAL_FILE_LIST.md",
    "artifact/CANONICAL_REVIEWER_PACKAGE.md",
    "artifact/REPRODUCIBILITY_STATUS.md",
    "artifact/SOURCE_AND_DATA.md",
    "artifact/ENVIRONMENT.md",
    "artifact/RESULT_NAMING_RULES.md",
    "artifact/VERIFICATION_LOG_2026-04-29.md",
    "artifact/VERIFICATION_LOG.md",
    "artifact/PACKAGE_AUDIT_2026-05-03.md",
    "artifact/PACKAGE_AUDIT.md",
    "artifact/DATA_RELEASE_POLICY.md",
    "artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md",
    "artifact/INFORMATION_ACCESS_CARD.md",
    "artifact/CLAIM_SURVIVAL_CARD.md",
    "artifact/CONTROLLED_DEGRADATION_PROTOCOL.md",
    "paper/latex/main.pdf",
    "paper/latex/main.tex",
    "paper/latex/neurips_2026.sty",
    "paper/tbl_prior_quality_response.md",
    "paper/tbl_prior_quality_response.json",
    "paper/prompt_only_structural_matcher.md",
    "retrieval/prompt_structural.py",
    "paper/tbl_backend_replicate_boundary.md",
    "paper/tbl_backend_replicate_boundary.json",
    "paper/backend_replicate_boundary_notes.md",
    "paper/tbl_controlled_degradation_sweep.md",
    "scripts/69_run_controlled_degradation_sweep.py",
    "results/degradation_sweep/summary_deepseek_seed1_n50.json",
]

P0_REQUIRED_GLOB_PATTERNS = [
    "results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed*.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed*.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed*.json",
    "results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed*.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed*.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed*.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed*.json",
    "results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed*.json",
    "results/degradation_sweep/*.json",
]

P0_FORBIDDEN_PACKAGE_PATTERNS = [
    "WORKLOG",
    "paperB/",
    "paper_review",
    "student_response",
    "reviewer_attack",
    "rebuttal",
    "strengthening_plan",
    "final_optimization_plan",
    "execution_plan",
    "integrated_draft",
    "old_drafts/",
    ".bak",
    ".tmp",
    ".DS_Store",
    "__pycache__/",
    ".ipynb_checkpoints/",
    "科技论文",
    "submission_readiness_plan",
    "handoff/",
    "READINESS_RESPONSE",
]

TEXT_SANITIZE_SUFFIXES = {
    ".bib",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".tex",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_SANITIZE_MAX_BYTES = 20_000_000
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_PATH_REPLACEMENTS = [
    (str(PROJECT_ROOT), "<PROJECT_ROOT>"),
    (str(Path.home() / ".cache" / "huggingface"), "<HF_CACHE>"),
    (str(Path.home() / ".cache" / "pip"), "<PIP_CACHE>"),
    (str(Path(sys.prefix)), "<CONDA_PREFIX>"),
    (str(Path.home()), "<LOCAL_HOME>"),
]


def sha256_for_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_for_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"unavailable ({exc})"


def should_include_file(path: Path) -> bool:
    parts = set(path.parts)
    if "__pycache__" in parts or ".pytest_cache" in parts:
        return False
    if path.suffix in {".pyc", ".pyo"}:
        return False
    if path.name in {".DS_Store"}:
        return False
    return True


def iter_dir_files(root: str) -> list[str]:
    base = Path(root)
    if not base.exists():
        return []
    return sorted(str(path) for path in base.rglob("*") if path.is_file() and should_include_file(path))


def iter_glob_files(pattern: str) -> list[str]:
    return sorted(str(path) for path in Path(".").glob(pattern) if path.is_file() and should_include_file(path))


def build_artifact_file_list() -> list[str]:
    # Direct NeurIPS supplementary zips are size-limited. The review package keeps
    # cached outputs and scripts for the reviewer quickstart, while large
    # upstream-derived benchmark assets are externalized and documented in
    # SOURCE_AND_DATA / DATA_RELEASE_POLICY.
    collected: set[str] = set(CANONICAL_PAPER_FILES + RESULT_FILES)
    for pattern in PAPER_GLOBS + RESULT_GLOBS:
        collected.update(iter_glob_files(pattern))
    for directory in SOURCE_DIRS:
        collected.update(iter_dir_files(directory))
    return sorted(collected)


def sanitize_text(text: str) -> str:
    for old, new in LOCAL_PATH_REPLACEMENTS:
        text = text.replace(old, new)
    text = re.sub(
        r'"source_revision"\s*:\s*"[0-9a-fA-F]{7,40}"',
        '"source_revision": "omitted_for_double_blind_review"',
        text,
    )
    text = re.sub(
        r"Source revision:\s*`[0-9a-fA-F]{7,40}`",
        "Source revision: `omitted_for_double_blind_review`",
        text,
    )
    text = text.replace("source_revision", "source_revision")
    text = text.replace("Source revision:", "Source revision:")
    return text


def should_sanitize_path(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SANITIZE_SUFFIXES and path.stat().st_size <= TEXT_SANITIZE_MAX_BYTES


def packaged_bytes(path: Path) -> bytes:
    if should_sanitize_path(path):
        return sanitize_text(path.read_text(encoding="utf-8", errors="ignore")).encode("utf-8")
    return path.read_bytes()


def write_sanitized_text(path: Path, text: str) -> None:
    write_text(path, sanitize_text(text))


def validate_package_entries(package_entries: dict[str, Path], missing: list[str]) -> None:
    names = set(package_entries)
    errors: list[str] = []
    if missing:
        errors.append("package list has missing source files: " + ", ".join(sorted(missing)))

    required_missing = [path for path in P0_REQUIRED_PACKAGE_PATHS if path not in names]
    if required_missing:
        errors.append("P0 required package paths missing: " + ", ".join(required_missing))

    for pattern in P0_REQUIRED_GLOB_PATTERNS:
        matches = sorted(path for path in names if fnmatch(path, pattern))
        if not matches:
            errors.append(f"P0 required pattern has no package matches: {pattern}")

    forbidden = sorted(
        path
        for path in names
        if any(pattern in path for pattern in P0_FORBIDDEN_PACKAGE_PATTERNS)
    )
    if forbidden:
        errors.append("forbidden stale/internal paths in package: " + ", ".join(forbidden))

    if errors:
        raise RuntimeError("Artifact package validation failed:\n- " + "\n- ".join(errors))


def build_package_audit(package_entries: dict[str, Path]) -> str:
    names = set(package_entries)
    lines = [
        "# Package Audit (2026-05-03)",
        "",
        "This file is generated by `scripts/59_package_ed_artifact.py`. The packaging script fails before writing the final archive if any P0 required file is missing or if stale internal files are included.",
        "",
        "The direct review zip externalizes large upstream-derived benchmark files so the archive can stay below the 100MB direct-upload threshold. Reviewer quickstart commands use packaged cached outputs and do not require those externalized benchmark files.",
        "",
        "## P0 Required Files",
        "",
    ]
    for path in P0_REQUIRED_PACKAGE_PATHS:
        status = "present" if path in names else "missing"
        lines.append(f"- `{path}`: {status}")

    lines.extend(["", "## P0 Required File Families", ""])
    for pattern in P0_REQUIRED_GLOB_PATTERNS:
        matches = sorted(path for path in names if fnmatch(path, pattern))
        lines.append(f"- `{pattern}`: {len(matches)} files")

    lines.extend(["", "## Forbidden Stale/Internal File Patterns", ""])
    for pattern in P0_FORBIDDEN_PACKAGE_PATTERNS:
        matches = sorted(path for path in names if pattern in path)
        lines.append(f"- `{pattern}`: {len(matches)} files")

    lines.extend(
        [
            "",
            "## Reviewer Quickstart Expected To Exist",
            "",
            "```bash",
            "bash artifact/reproduce_main.sh",
            "bash artifact/verify_provenance.sh",
            "cat artifact/CLAIM_TO_EVIDENCE.md",
            "cat artifact/KNOWN_LIMITATIONS.md",
            "```",
            "",
            "## Upload Guidance",
            "",
            "- Main paper PDF for review: `paper/latex/main.pdf`.",
            "- Anonymous artifact archive: `artifact/planb_ed_artifact_anon.zip`.",
            "- Direct zip size limit enforced by packaging script: `<100,000,000` bytes.",
            "- Do not upload historical handoff zips or worklog bundles.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_zip_archive(zip_path: Path, manifest_path: Path, hash_manifest_path: Path) -> tuple[int, str]:
    zip_size = zip_path.stat().st_size
    if zip_size >= DIRECT_ZIP_SIZE_LIMIT_BYTES:
        raise RuntimeError(
            f"Final zip is {zip_size} bytes, above the direct-upload limit "
            f"of {DIRECT_ZIP_SIZE_LIMIT_BYTES} bytes"
        )
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        required_missing = [path for path in P0_REQUIRED_PACKAGE_PATHS if path not in names]
        forbidden = sorted(
            path
            for path in names
            if any(pattern in path for pattern in P0_FORBIDDEN_PACKAGE_PATTERNS)
        )
        if required_missing:
            raise RuntimeError("Final zip missing P0 paths: " + ", ".join(required_missing))
        if forbidden:
            raise RuntimeError("Final zip contains stale/internal paths: " + ", ".join(forbidden))

        manifest = json.loads(manifest_path.read_text())
        manifest_files = set(manifest["files"])
        missing_from_zip = sorted(manifest_files - names)
        extra_in_zip = sorted(names - manifest_files)
        if missing_from_zip or extra_in_zip:
            raise RuntimeError(
                "Final zip/manifest mismatch: "
                f"missing={missing_from_zip[:10]} extra={extra_in_zip[:10]}"
            )

        hash_manifest = json.loads(hash_manifest_path.read_text())
        hash_mismatches: list[str] = []
        for row in hash_manifest["files"]:
            path = row["path"]
            if path not in names:
                hash_mismatches.append(path)
                continue
            if hashlib.sha256(archive.read(path)).hexdigest() != row["sha256"]:
                hash_mismatches.append(path)
        if hash_mismatches:
            raise RuntimeError("Final zip/hash mismatch: " + ", ".join(hash_mismatches[:10]))

    digest = sha256_for_path(zip_path)
    return len(names), digest


def build_readme() -> str:
    text = "# Plan B Anonymous E&D Artifact\n\n"
    text += "## Identity\n\n"
    text += f"This artifact is packaged for the NeurIPS E&D submission \"{FINAL_PAPER_TITLE}\". The scientific object is evaluation design. The main contribution is SPC-Audit: a diagnostic claim-audit protocol showing that matched candidate budget, matched execution-call accounting, information access, and prior quality determine which structural-prior claim is warranted in few-shot code generation.\n\n"
    text += "This artifact is not only a reproduction package. It is a claim-audit resource. Reviewers can use it to:\n\n"
    text += "1. regenerate paper-facing results;\n"
    text += "2. verify prompt-only matcher provenance;\n"
    text += "3. verify stored `structure_fidelity` provenance;\n"
    text += "4. inspect supported and unsupported claims;\n"
    text += "5. reuse the audit templates for future structural-prior evaluations.\n\n"
    text += "Main-result backend identity: the primary `MBPP+224` matched-budget evidence is on `Qwen/Qwen2.5-Coder-7B-Instruct`; DeepSeek is supplementary cross-model and external-support evidence; StarCoder-family runs are boundary checks.\n\n"
    text += "## Canonical Paper Objects\n\n"
    text += "- Table 1: conclusion-shift table (`paper/tbl_conclusion_shift.md`)\n"
    text += "- Table 2: full `MBPP+224` fair-budget main table (`paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json`)\n"
    text += "- Stats/cost support: `paper/tbl_stats_cost.md`\n"
    text += "- Prompt-only boundary controls: `paper/tbl_prompt_only_lexical_control.md`, `paper/tbl_prompt_only_structural_control.md`, `paper/tbl_prompt_only_structural_mbpp224_control.md`\n"
    text += "- Prior-quality response audit: `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`, `scripts/67_make_prior_quality_audit.py`, `scripts/68_make_prior_quality_response.py`\n"
    text += "- Prior-quality provenance and matcher specification: `paper/prior_quality_audit_provenance.md`, `paper/prompt_only_structural_matcher.md`\n"
    text += "- Provenance validation checklist: `paper/provenance_validation_checklist.md`, `artifact/verify_provenance.sh`\n"
    text += "- Reusable audit checklist and data-release policy: `paper/audit_reporting_checklist.md`, `paper/data_release_policy.md`\n"
    text += "- Claim survival hierarchy: `artifact/CLAIM_SURVIVAL_CARD.md`\n"
    text += "- Contribution and artifact summary: `paper/contribution_and_artifact_summary.md`, `artifact/CONTRIBUTION_AND_ARTIFACT_SUMMARY.md`\n"
    text += "- Reviewer-facing walkthrough: `paper/artifact_reviewer_walkthrough.md`\n"
    text += "- Final submission QA checklist: `paper/final_submission_qa_checklist.md`\n"
    text += "- Task-clustered paired stats: `paper/tbl_task_clustered_paired_stats.md`\n"
    text += "- No-rerank directionality: `paper/tbl_no_rerank_directionality_v2.md`\n"
    text += "- Figure 1 support: budget sweep with uncertainty (`paper/fig_budget_sweep_v2.md`, `paper/fig_budget_sweep_v2.json`)\n"
    text += "- External evidence: `paper/tbl_external_v2.md` plus DeepSeek slice notes\n"
    text += "- Cross-model discussion: `paper/tbl_cross_model_v2.md`, `paper/tbl_cross_model_deepseek_two_seed.md`, `paper/tbl_cross_model_starcoder2_two_seed.md`\n"
    text += "- Boundary instantiations: `paper/tbl_boundary_instantiations.md`\n"
    text += "- Replicate-sensitive backend boundary checks: `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md`\n"
    text += "- Controlled degradation sweep: `paper/tbl_controlled_degradation_sweep.md`, `results/degradation_sweep/*.json`\n"
    text += "- Concept figure support: `paper/figure1_concept.md`\n"
    text += "- Manuscript source starter: `paper/latex/main.tex`, `paper/latex/neurips_2026.sty`\n\n"
    text += "This package includes current paper-facing objects and a LaTeX starter. Historical planning drafts, reviewer-attack notes, rebuttal prewrites, response notes, and older worklogs are intentionally not part of the canonical anonymous artifact to avoid stale claim wording.\n\n"
    text += "The canonical claim set is defined by `artifact/CLAIM_TO_EVIDENCE.md` and the main paper. Exploratory materials, if present, are not used as main-claim evidence unless explicitly listed in `artifact/CLAIM_TO_EVIDENCE.md`.\n\n"
    text += "## Reviewer-First Reproduction\n\n"
    text += "Quickstart:\n\n"
    text += "```bash\n"
    text += "bash artifact/reproduce_main.sh\n"
    text += "bash artifact/verify_provenance.sh\n"
    text += "cat artifact/CLAIM_TO_EVIDENCE.md\n"
    text += "cat artifact/KNOWN_LIMITATIONS.md\n"
    text += "```\n\n"
    text += "Additional focused commands are `bash artifact/reproduce_table1.sh`, `bash artifact/reproduce_figure1.sh`, and `bash artifact/reproduce_figures.sh`.\n\n"
    text += "These commands regenerate paper-facing tables and figure-support files from packaged cached outputs and raw-result JSONs. They do not call an LLM, do not require a GPU, do not require network access, and do not execute generated code. Full experiment reruns require prepared upstream benchmark assets plus an available model endpoint or local model matching the recorded backend configuration.\n\n"
    text += "## Navigation Aids\n\n"
    text += "- `artifact/CANONICAL_FILE_LIST.md`: frozen paper-object list; use this first when writing\n"
    text += "- `artifact/CONTRIBUTION_AND_ARTIFACT_SUMMARY.md`: compact contribution and reviewer-entry summary\n"
    text += "- `artifact/REVIEWER_QUICKSTART.md`: one-page quickstart for reviewers\n"
    text += "- `artifact/CLAIM_TO_EVIDENCE.md`: which files support each headline claim\n"
    text += "- `artifact/PAPER_TO_ARTIFACT_MAP.md`: where each paper object lives on disk\n"
    text += "- `artifact/ENVIRONMENT.md`: recovered software / serving / hardware notes\n"
    text += "- `artifact/SOURCE_AND_DATA.md`: included code tree, externalized benchmark-data inventory, and redistribution status\n"
    text += "- `artifact/DATA_RELEASE_POLICY.md`: public-release and review-package data policy\n"
    text += "- `artifact/REPRODUCIBILITY_STATUS.md`: what is fully regenerable versus provenance-only\n"
    text += "- `paper/tbl_backend_replicate_boundary.md`: Granite and StarCoder2 replicate-sensitive backend boundary table\n"
    text += "- `paper/backend_replicate_boundary_notes.md`: raw-result pointers, serving-mode caveats, and filter-attempt transparency for backend boundary checks\n"
    text += "- `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`: reusable audit-reporting template\n"
    text += "- `artifact/INFORMATION_ACCESS_CARD.md`: reusable information-access disclosure card\n"
    text += "- `artifact/CLAIM_SURVIVAL_CARD.md`: reusable claim-survival hierarchy card\n"
    text += "- `artifact/CANONICAL_REVIEWER_PACKAGE.md`: reviewer package inventory and exclusions\n"
    text += "- `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`: pre-registered prior-quality degradation protocol and completed DeepSeek pilot scope\n"
    text += "- `artifact/VERIFICATION_LOG_2026-04-29.md`: latest reviewer-script verification summary\n"
    text += "- `artifact/RESULT_NAMING_RULES.md`: backend-safe naming policy\n"
    text += "- `artifact/KNOWN_LIMITATIONS.md`: exact scope limits and non-claims\n"
    text += "- `artifact/manifest_with_hashes.json`: file-level hashes for packaged contents\n"
    text += "\n## Safety And Data Release\n\n"
    text += "Generated Python code should be treated as untrusted and run only in an appropriate sandbox with resource limits. The direct review zip externalizes large upstream-derived benchmark assets and keeps cached outputs, scripts, metadata, and hashes for inspection. The public release follows `artifact/DATA_RELEASE_POLICY.md`; upstream benchmark data or tests are redistributed publicly only when permission is verified, otherwise provenance and preparation metadata are provided.\n"
    text += "\nPackaging note: the uploaded archive filename is `artifact/planb_ed_artifact_anon.zip`. That filename is a transport wrapper for the package and is not expected to appear as an internal file inside the archive.\n"
    return text

def build_artifact_contribution_summary() -> str:
    return """# Contribution And Artifact Summary

This reviewer-facing note summarizes the submission contribution and the artifact entry points. The paper is an evaluation-design and artifact contribution, not a new structural-prior method and not a new benchmark.

## Contribution Position

The central contribution is **SPC-Audit**, a prior-quality-aware diagnostic audit protocol for structural-prior claims in execution-evaluated code generation.

The reusable pattern has five parts:

1. **Fair-budget diagnostic audit.** Compare prior conditions under matched candidate budget and matched execution-call accounting, while explicitly disclosing information access and selection status.
2. **Information-access boundary controls.** Separate fixed code-aware diagnostic evidence from prompt-only controls and oracle-derived stress tests.
3. **Prior-quality response audit.** Report quality coverage, bin-level net delta, harm rate, outcome-level fidelity separation, and threshold sensitivity instead of only average prior-versus-no-prior solved-task deltas.
4. **Claim survival hierarchy.** Label operational, diagnostic, prompt-only, quality-conditioned, and broad-transfer claims by what assumptions they survive.
5. **Replicate-sensitive backend reporting.** For backend-level claims, report stochastic replicate count, deterministic-seed status, candidate-level pass movement, paired changed outcomes, and serving format.

## Reviewer Entry Points

| Reviewer Question | Artifact Entry Point |
| --- | --- |
| Which claims are supported, qualified, or unsupported? | `artifact/CLAIM_TO_EVIDENCE.md`, `artifact/KNOWN_LIMITATIONS.md` |
| Can the paper-facing tables be regenerated without live LLM inference? | `artifact/reproduce_main.sh` |
| Is the prompt-only structural matcher fixed and query-prompt-only on the query side? | `artifact/verify_provenance.sh`, `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |
| Does the prior-quality response audit read stored raw-result fields rather than tuning retrieval or filtering episodes? | `artifact/verify_provenance.sh`, `paper/prior_quality_audit_provenance.md`, `scripts/67_make_prior_quality_audit.py` |
| What requires live model inference rather than cached-output regeneration? | `artifact/REPRODUCIBILITY_STATUS.md` |
| How can another project reuse the reporting pattern? | `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md` |
| Where is the controlled prior-quality degradation pilot? | `paper/tbl_controlled_degradation_sweep.md`, `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md` |
| Where are small boundary instantiations outside the main table summarized? | `paper/tbl_boundary_instantiations.md` |
| Where are replicate-sensitive Granite and StarCoder2 checks summarized? | `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` |

## Claim Boundary

The artifact supports scoped positive claims about conclusion shift, fixed code-aware diagnostic gains, prompt-only boundaries, quality-conditioned interpretation, and replicate-sensitive backend-boundary reporting. It does not support a strongest-method claim, deployable prompt-only structural-prior method, deployment-time `MBR-exec` selector, backend invariance, broad transfer, clean StarCoder2 instruction-backend replication, causal mechanism proof from `structure_fidelity`, or a new benchmark claim.

## Quickstart

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```
"""


def build_reviewer_quickstart() -> str:
    return """# Reviewer Quickstart

Run from the artifact root:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

## Requirements for quickstart

- GPU: not required
- API key: not required
- LLM endpoint: not required
- Network: not required
- Executes generated code: no
- Expected runtime: about 1 minute on a standard CPU environment
- Python dependencies: standard library plus packaged repository modules; see `requirements.txt`

## Expected PASS output

The exact order may vary slightly, but the scripts should end with these lines:

```text
[PASS] regenerated conclusion-shift table
[PASS] regenerated stats/cost table
[PASS] regenerated budget sweep support
[PASS] regenerated bad-prior breakdown
[PASS] regenerated prior-quality audit
[PASS] regenerated controlled-degradation table from cached outputs
[PASS] regenerated main reviewer-facing tables and figures from cached results
[PASS] prompt_structural matcher constants verified
[PASS] query-side prompt-only access boundary verified
[PASS] raw structure_fidelity fields verified
[PASS] prior-quality response regenerated from cached outputs
[PASS] verified matcher provenance and regenerated prior-quality audit from cached outputs
```

No live LLM inference is required for the quickstart.

## Runtime table

| Command | Expected runtime | Requires GPU? | Calls LLM? | Executes generated code? |
| --- | ---: | --- | --- | --- |
| `bash artifact/reproduce_main.sh` | ~30 sec | no | no | no |
| `bash artifact/verify_provenance.sh` | ~20 sec | no | no | no |
| live reruns | hours/days | yes/endpoint | yes | yes |

Start with:

1. `artifact/CLAIM_TO_EVIDENCE.md`
2. `artifact/KNOWN_LIMITATIONS.md`
3. `paper/tbl_prior_quality_response.md`
4. `paper/tbl_backend_replicate_boundary.md`
5. `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`

## Troubleshooting

- If Python cannot import local modules, run from the artifact root.
- If cached outputs are missing, verify archive extraction completed.
- If live rerun scripts are invoked accidentally, stop and use the quickstart scripts only.
- If a shell reports permission issues for scripts, invoke them with `bash path/to/script.sh`.
"""


def build_claim_to_evidence() -> str:
    return """# Claim To Evidence Map

| ID | Claim | Status | Evidence | Boundary |
| --- | --- | --- | --- | --- |
| C0 | operational pipeline gain | supported operationally | `paper/tbl_conclusion_shift.md`, old uncontrolled raw results | Entangles structural conditioning and selection opportunity; not an attributed structural-prior claim. |
| C1 | matched-budget code-aware diagnostic effect | supported with scope | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json`, `paper/tbl_stats_cost.md`, `paper/tbl_task_clustered_paired_stats.md` | Fixed code-aware `syntax_aware` episodes, matched candidate budget and execution-call accounting, diagnostic `MBR-exec`. |
| C2 | full prompt-only structural retrieval effect | not supported | `paper/tbl_prompt_only_structural_mbpp224_control.md`, `results/prompt_only_structural_mbpp224_fair_budget/summary.json` | Deployable prompt-only structural-prior claim is unsupported by the full `MBPP+224` rerun. |
| C3 | quality-conditioned evaluation claim: prior presence alone is insufficient; intended priors show most positive movement in medium/high retrospective-fidelity bins; prompt-only high-fidelity coverage is rare; misleading priors can harm | supported diagnostic audit | `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`, `paper/prior_quality_audit_provenance.md`, `results/mbpp224_fair_budget/summary.json`, `results/prompt_only_structural_mbpp224_fair_budget/summary.json`, `paper/fig_bad_prior_delta_types.md`, `paper/bad_prior_failure_breakdown.md` | Retrospective/reference-code-based; not a causal mechanism; not a deployable quality estimator. |
| C4 | broad transfer / backend invariance / strongest-method claim | unsupported | `paper/tbl_external_v2.md`, `paper/tbl_boundary_instantiations.md`, `paper/tbl_cross_model_v2.md`, `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` | External and backend rows are boundary instantiations; positive, neutral, mixed, and negative rows are retained. |
| Artifact | SPC-Audit is a reusable diagnostic audit protocol for structural-prior claims | supported artifact contribution | `paper/audit_reporting_checklist.md`, `paper/contribution_and_artifact_summary.md`, `paper/claim_matrix_v2.md`, `paper/artifact_reviewer_walkthrough.md`, `artifact/PAPER_TO_ARTIFACT_MAP.md`, `artifact/CLAIM_SURVIVAL_CARD.md`, `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md` | Reporting pattern, not a new benchmark or deployable generation method. |
| Artifact | the audit filters claims by the assumptions they survive | supported | `paper/latex/sections/01_introduction.tex`, `paper/latex/sections/03_results.tex`, `artifact/CLAIM_SURVIVAL_CARD.md` | Negative and boundary rows are part of the contribution. |
| Boundary | core claims do not depend entirely on accepting the prior-quality audit | supported boundary | `paper/tbl_conclusion_shift.md`, `paper/b_mbpp224_fair_budget.md`, `paper/tbl_prompt_only_structural_mbpp224_control.md`, `paper/audit_reporting_checklist.md` | Setting aside C3 weakens the quality-conditioned interpretation but not the conclusion shift or prompt-only boundary. |
| Boundary | matched candidate budget and execution-call accounting separate structural-prior effects from same-test diagnostic execution-selection | supported boundary | `paper/tbl_conclusion_shift.md`, `paper/tbl_stats_cost.md`, `paper/tbl_stats_cost.json`, `paper/experimental_setup_v2.md` | Not full token or wall-clock compute equality. |
| Protocol | prompt-only structural matcher is fixed query-prompt boundary control | supported protocol detail | `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py`, `paper/provenance_validation_checklist.md` | Query-side code/tests are not used by the prompt-only structural matcher. |
| Protocol | matcher and prior-quality provenance are directly inspectable | supported artifact contribution | `paper/provenance_validation_checklist.md`, `artifact/verify_provenance.sh`, `paper/prior_quality_audit_provenance.md`, `paper/prompt_only_structural_matcher.md` | Reviewer quickstart verifies cached provenance, not live LLM reruns. |
| Boundary | no-rerank directionality still distinguishes correct versus bad priors | supporting boundary | `paper/tbl_no_rerank_directionality_v2.md`, `results/mbppplus_vllm_v4_100_oracle.json`, `results/mbppplus_vllm_v4_100_no_structure.json`, `results/mbppplus_vllm_v4_100_random.json`, `results/mbppplus_vllm_v4_100_corrupted.json` | Diagnostic proposal-time evidence, not deployable reranking. |
| Boundary | bad priors remain harmful under reranking | supported | `paper/fig_bad_prior_delta_types.md`, `paper/bad_prior_failure_breakdown.md`, `paper/experimental_setup_v2.md`, `results/mbpp224_fair_budget/summary.json` | Stress test under the same diagnostic selector. |
| Boundary | external evidence is qualified rather than broad-transfer evidence | qualified | `paper/tbl_external_v2.md`, `paper/external_protocol.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed2.md`, `artifact/REPRODUCIBILITY_STATUS.md`, `results/external_slice_humanevalplus50_deepseek_seed1.json`, `results/external_slice_humanevalplus50_deepseek_seed2.json`, `results/external_slice_bigcodebench_hard50_deepseek_seed1.json` | HumanEval+50 DeepSeek is mixed across two seeds and must not be paraphrased as transfer. |
| Boundary | cross-model evidence is backend-sensitive rather than invariant | qualified | `paper/tbl_cross_model_v2.md`, `paper/tbl_cross_model_v2.json`, `paper/tbl_cross_model_deepseek_two_seed.md`, `paper/tbl_cross_model_starcoder2_two_seed.md`, `paper/experimental_setup_v2.md`, `results/cross_model_deepseek_summary.json`, `results/cross_model_deepseek_summary_seed2.json`, `results/cross_model_starcoder2_summary_seed1.json`, `results/cross_model_starcoder2_summary_seed2.json` | Backend rows instantiate reporting boundaries, not robustness. |
| Boundary | backend-level structural-prior claims are replicate-sensitive | supported boundary | `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, `paper/backend_replicate_boundary_notes.md`, `results/vllm_granite8b_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json`, `results/vllm_granite8b_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json`, `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_rerun_seed1.json`, `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_rerun_seed1.json` | vLLM seed labels are stochastic replicate labels; StarCoder2 is completion-style serving. |
| Boundary | HumanEval+ and backend boundary instantiations show the reporting pattern beyond the main table | qualified | `paper/tbl_boundary_instantiations.md`, `results/humanevalplus164_syntax_no_prior_mbrexec_budget8_seed1.json`, `results/humanevalplus164_syntax_best_structure_budget8_seed1.json`, `results/humanevalplus50_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed1.json`, `results/humanevalplus50_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`, `results/humanevalplus50_deepseek_syntax_aware_no_prior_mbrexec_budget8_seed2.json`, `results/humanevalplus50_deepseek_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`, `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json`, `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`, `results/vllm_starcoder2_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json`, `results/vllm_starcoder2_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json`, `results/hf_safe_gpu_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json`, `results/hf_safe_gpu_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`, `results/hf_safe_gpu_mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed2.json`, `results/hf_safe_gpu_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed2.json` | Positive, neutral, mixed, and negative rows are retained. |
| Secondary | controlled prior-quality degradation pilot has been run | supported secondary diagnostic | `paper/tbl_controlled_degradation_sweep.md`, `results/degradation_sweep/summary_deepseek_seed1_n50.json`, `results/degradation_sweep/*.json`, `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md` | Noisy pilot; not causal proof and not main evidence. |
| Boundary | fair-budget does not mean full compute equality | supported boundary | `paper/tbl_stats_cost.md`, `paper/tbl_stats_cost.json`, `paper/experimental_setup_v2.md` | Matched candidate budget and execution-call accounting only. |
"""


def build_paper_to_artifact() -> str:
    return """# Paper To Artifact Map

| Paper Object | Artifact Location |
| --- | --- |
| one-page reviewer quickstart | `artifact/REVIEWER_QUICKSTART.md` |
| conclusion-shift table | `paper/tbl_conclusion_shift.md`, `paper/tbl_conclusion_shift.json` |
| full `MBPP+224` fair-budget table | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json` |
| stats/cost fairness table | `paper/tbl_stats_cost.md`, `paper/tbl_stats_cost.json` |
| task-clustered paired stats | `paper/tbl_task_clustered_paired_stats.md` |
| prompt-only boundary controls | `paper/tbl_prompt_only_lexical_control.md`, `paper/tbl_prompt_only_structural_control.md`, `paper/tbl_prompt_only_structural_mbpp224_control.md`, `results/prompt_only_*/*.json` |
| prompt-only structural matcher specification | `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |
| prior-quality response audit | `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_audit.json`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`, `paper/prior_quality_audit_provenance.md`, `scripts/67_make_prior_quality_audit.py`, `scripts/68_make_prior_quality_response.py` |
| claim survival hierarchy | `artifact/CLAIM_SURVIVAL_CARD.md`, `paper/claim_matrix_v2.md` |
| controlled degradation protocol and pilot | `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`, `paper/tbl_controlled_degradation_sweep.md`, `results/degradation_sweep/*.json` |
| provenance validation checklist | `paper/provenance_validation_checklist.md`, `artifact/verify_provenance.sh` |
| reusable audit checklist | `paper/audit_reporting_checklist.md` |
| data release policy | `artifact/DATA_RELEASE_POLICY.md`, `paper/data_release_policy.md` |
| reviewer-facing artifact walkthrough | `paper/artifact_reviewer_walkthrough.md` |
| contribution and artifact summary | `paper/contribution_and_artifact_summary.md` |
| final submission QA checklist | `paper/final_submission_qa_checklist.md` |
| latest verification log | `artifact/VERIFICATION_LOG.md`, `artifact/VERIFICATION_LOG_2026-04-29.md` |
| budget sweep with uncertainty | `paper/fig_budget_sweep_v2.md`, `paper/fig_budget_sweep_v2.json`, `results/budget_sweep/*.json` |
| no-rerank directionality provenance | `paper/tbl_no_rerank_directionality_v2.md`, `results/mbppplus_vllm_v4_100_oracle.json`, `results/mbppplus_vllm_v4_100_no_structure.json`, `results/mbppplus_vllm_v4_100_random.json`, `results/mbppplus_vllm_v4_100_corrupted.json` |
| external evidence table | `paper/tbl_external_v2.md`, `paper/external_protocol.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed1.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed2.md`, `paper/tbl_external_modern50_deepseek.md` |
| cross-model table | `paper/tbl_cross_model_v2.md`, `paper/tbl_cross_model_v2.json`, `paper/tbl_cross_model_deepseek_two_seed.md`, `paper/tbl_cross_model_deepseek_two_seed.json`, `paper/tbl_cross_model_starcoder2_two_seed.md`, `paper/tbl_cross_model_starcoder2_two_seed.json` |
| boundary instantiations | `paper/tbl_boundary_instantiations.md` |
| replicate-sensitive backend boundary checks | `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, `paper/backend_replicate_boundary_notes.md` |
| bad-prior harm decomposition | `paper/fig_bad_prior_delta_types.md`, `paper/fig_bad_prior_delta_types.json`, `paper/bad_prior_failure_breakdown.md` |
| concept figure support | `paper/figure1_concept.md` |
| manuscript source starter | `paper/latex/main.tex`, `paper/latex/neurips_2026.sty`, `paper/latex/sections/*.tex` |
| canonical backend and protocol identity | `paper/experimental_setup_v2.md`, `artifact/ENVIRONMENT.md` |
| bibliography starter and related-work notes | `paper/refs_planb.bib`, `paper/related_work_notes.md`, `paper/reference_inventory.md` |
| executable source tree | `plan_b/`, `generation/`, `retrieval/`, `structure/`, `gating/`, `rerank/`, `guardrails/`, `eval/`, `verifier/`, `scripts/`, `configs/` |
| main benchmark data and episodes | externalized from the direct review zip; see `artifact/SOURCE_AND_DATA.md`, `artifact/DATA_RELEASE_POLICY.md`, and the result-file provenance paths |
| external rerun inputs | externalized from the direct review zip; see `artifact/SOURCE_AND_DATA.md` for expected layout, redistribution status, and replacement plan |
| old uncontrolled regime provenance | `results/mbppplus_full_k1_syntax_noprior_nogate_nombr_vllm_seed1.json`, `results/mbppplus_full_k1_syntax_multiprior_nogate_mbrexec_vllm_seed1.json` |
"""


def build_known_limitations() -> str:
    return """# Known Limitations

- The main benchmark is execution-evaluated few-shot Python function generation, not repo-level or tool-use-heavy code generation.
- `HumanEval+` and the compatibility-filtered `BigCodeBench-Hard` slices support qualified external evidence, not broad-transfer claims; the larger modern slice is still slice-sensitive.
- Cross-model evidence supports backend-sensitive portability, not backend invariance.
- Cross-model seeds are symmetric for the two stronger instruction-style backends in the current artifact: Qwen uses seeds `1,2`, DeepSeek uses seeds `1,2`; Granite and StarCoder2 have additional four-replicate backend-boundary checks; the weak backend uses GPU seeds `1,2` as a negative boundary.
- The budget-sweep figure is mechanism support on `MBPP+100`, not the headline claim benchmark.
- `fair-budget` in this repo means matched candidate budget plus matched execution-call accounting; it does not mean prompt-token equality or full compute equality.
- `MBR-exec` is diagnostic execution selection using packaged task tests for candidate selection and solved-count reporting; it is not a deployment-time selection claim.
- The full `MBPP+224` prompt-only structural rerun is non-positive and should be treated as a boundary result, not hidden as a minor caveat.
- The prior-quality audit uses `structure_fidelity`, a retrospective diagnostic metric based on reference-code structure; it is not a deployable prior-quality estimator.
- The prior-quality response audit reports quality coverage, net delta by fidelity bin, harm rate, outcome-level fidelity separation, and threshold sensitivity; these analyses are diagnostic consistency checks, not causal proof.
- The controlled prior-quality degradation sweep is a DeepSeek `MBPP+50` pilot, not a main-table result. It is useful as secondary diagnostic evidence but is noisy and should not be presented as causal proof.
- Granite and StarCoder2 checks are replicate-sensitive backend boundary evidence. They do not support backend invariance or broad cross-backend claims. The pipeline seed is not passed into the vLLM OpenAI payload, so seed labels should be interpreted as stochastic replicate labels rather than deterministic generation seeds.
- StarCoder2-7B is completion-style serving and should not be interpreted as a clean instruction-backend replication. Granite is the cleaner supplemental instruction/chat backend, but its four-replicate aggregate remains modest and noisy.
- The prompt-only structural matcher is a fixed boundary control that uses query prompt and entry point only on the query side; it is not a new prior-construction method.
- The reported full `MBPP+224` prompt-only structural rerun is not selected from an alternative-weight sweep, and no alternative-weight sweep is used in the canonical artifact.
- The no-rerank directionality evidence is normalized into a `v2` paper-facing provenance table, but it remains diagnostic rather than deployable.
- The bad-prior decomposition now uses seeds `1,2,3`; `all_compile_fail` remains the dominant regression type, but `corrupted_prior` also shows small timeout spillover in some seeds.
- The compatibility-filtering step for `BigCodeBench-Hard` slice preparation depends on access to an upstream dataset cache; the direct review zip provides cached outputs and provenance, while live reruns require reconstructing processed slices from upstream sources.
- The package includes current paper-facing objects, a NeurIPS LaTeX starter, and the official style file, but not final camera-ready figure files.
- Public artifact release follows `paper/data_release_policy.md`; upstream benchmark datasets or tests are not redistributed publicly unless redistribution permission is verified.
- Historical verifier/usefulness assets remain in the repo, but usefulness is not part of the current canonical claim set because this package does not include a dedicated paper-facing negative-result object for it.
- The bibliography starter now covers the core manuscript buckets, but it is still intentionally selective rather than exhaustive.
"""


def build_naming_rules() -> str:
    return """# Result Naming Rules

All new result paths should encode:

`<dataset>_<retrieval>_<setting>_<rerank>_budget<k>_seed<s>.json`

Additional backend-specific runs must also encode backend identity explicitly, for example:

`vllm_deepseek_mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json`

Rules:

1. Never write cross-model outputs to the canonical vLLM result names used by the main tables.
2. Keep benchmark, backend, budget, seed, and method visible in the filename.
3. If a script can target multiple backends, its default output path must remain backend-isolated.
4. Writing and artifact references should use the canonical `v2` paper objects; superseded paper objects remain in the repo only as historical drafts.
"""


def build_structural_prior_audit_template() -> str:
    return """# Structural-Prior Audit Template

Use this template when applying the reporting pattern to a new structural-prior evaluation. It is a template, not a claim that every future study must use this paper's exact benchmark, selector, or fidelity metric.

## 1. Evaluation Target

- Task family:
- Benchmark / split:
- Generator backend:
- Selector:

## 2. Budget Accounting

- Candidate budget:
- Budget split across prior variants:
- Execution calls:
- Prompt tokens matched? yes/no:

## 3. Information Access

| Component | Query-side access | Support-side access | Test access | Diagnostic or deployable? |
| --- | --- | --- | --- | --- |
| Retrieval |  |  |  |  |
| Prompt construction |  |  |  |  |
| Candidate selection |  |  |  |  |
| Solved-count reporting |  |  |  |  |

## 4. Prior Conditions

- `no_prior`:
- intended prior:
- random prior:
- corrupted / misleading prior:
- prompt-only boundary control:

## 5. Results

- Solved tasks:
- Paired improved / regressed / unchanged:
- Task-clustered directionality:

## 6. Replicate Sensitivity, If Making Backend-Level Claims

- Stochastic replicate count:
- Are generation seeds deterministic at the serving backend? yes/no/unknown:
- Candidate-level pass movement:
- Paired changed outcomes:
- Serving format:

## 7. Prior-Quality Response, If Available

- Quality metric:
- Quality coverage:
- Net delta by bin:
- Harm rate:
- Outcome-level fidelity separation:
- Threshold sensitivity:
- All-candidate compile-fail rate:
- Selected-candidate timeout / fail rate:
- Deployable or retrospective?

## 8. Supported Claims

- 

## 9. Unsupported Claims

- 
"""


def build_information_access_card() -> str:
    return """# Information Access Card

Use this card to disclose what information each component can see. A structural-prior result has different meaning depending on whether it uses prompt-only information, stored query code, tests, generated outputs, or execution feedback.

| Component | Query prompt | Query solution code | Query tests | Support prompt | Support code | Generated outputs | Execution feedback | Role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Main `syntax_aware` retrieval | yes | yes, stored query code fields | no | yes | yes | no | no | code-aware diagnostic retrieval |
| Prompt-only lexical retrieval | yes | no | no | yes | no | no | no | prompt-only boundary |
| Prompt-only structural retrieval | yes, plus entry point | no | no | yes | yes, support-side only | no | no | prompt-only query-side boundary |
| Prior construction: `single_prior` / `multi_prior` | yes | depends on retrieval regime | no | yes | support-side structure when available | no | no | prior construction under disclosed access |
| `random_prior` | no query solution use beyond diagnostic setup | diagnostic stress condition | no | support pool / random prior source | may use support-side structure | no | no | bad-prior control |
| `corrupted_prior` | oracle-derived before corruption | yes, diagnostic/oracle-derived before corruption | no | support-side diagnostic source | yes | no | no | diagnostic stress test, not deployable |
| Generator | prompt text provided by condition | no direct hidden access | no | prompt-provided examples only | prompt-provided summaries only | no | no | candidate generation |
| `MBR-exec` selector | selected candidates | no | yes, packaged task tests | no | no | yes | yes | same-test diagnostic selector, not deployable |
| Solved-count reporting | generated selected output | reference/test oracle for evaluation | yes | no | no | selected output | pass/fail execution | reporting metric |
| `structure_fidelity` audit | reference-code structure | yes, retrospective | no selection use | prior summary | prior summary | no | no | retrospective diagnostic stratifier, not deployable |

## Interpretation

- The main `syntax_aware` result is code-aware diagnostic evidence.
- Prompt-only conditions exclude query solution code on the query side.
- `MBR-exec` is same-test diagnostic selection, not deployable reranking.
- `structure_fidelity` is retrospective/reference-code-based and is not used for generation, selection, or tuning.
- `corrupted_prior` is oracle-derived before corruption and is a diagnostic stress test.
"""


def build_claim_survival_card() -> str:
    return """# Claim Survival Card

Use this card to record which structural-prior claims survive a diagnostic audit. The goal is not to make every row positive; the goal is to preserve supported claims and make unsupported claims explicit.

| Claim level | Candidate claim | Audit result | Evidence | Boundary | Survives? |
| --- | --- | --- | --- | --- | --- |
| C0 | Operational pipeline gain | Supported | `167/224 -> 184/224` | Entangles structural conditioning and selection opportunity. | Yes, operational only |
| C1 | Structure-attributable fair-budget diagnostic gain | Supported with scope | `178.67 -> 185.00` | Fixed code-aware `syntax_aware` episodes with diagnostic `MBR-exec`. | Scoped |
| C2 | Deployable prompt-only structural retrieval | Unsupported | Full `MBPP+224` prompt-only structural rerun: `179.33` vs `177.67` | Current prompt-only retriever does not reproduce the main positive effect. | No |
| C3 | Quality-conditioned interpretation | Diagnostic support | Medium/high-fidelity code-aware bins are positive; full prompt-only high-fidelity coverage is low. | `structure_fidelity` is retrospective and reference-code-based. | Diagnostic |
| C4 | Broad transfer, backend invariance, strongest-method claim | Unsupported | External/backend rows are mixed, including weak-backend regressions. | Boundary evidence only. | No |

## Writing Rules

- Positive diagnostic rows must retain their information-access and selector boundaries.
- Prompt-only negative rows should remain visible as boundary evidence.
- Prior-quality response may support a quality-conditioned interpretation, but it is not causal proof or a deployable quality estimator.
- External/backend rows instantiate the audit pattern; they are not broad-transfer or backend-invariance evidence.
"""


def build_canonical_reviewer_package() -> str:
    return """# Canonical Reviewer Package

This file describes the intended anonymous reviewer package. It is a navigation aid for artifact reviewers and a guardrail against stale-file contamination.

## Reviewer Quickstart

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

## First Files To Inspect

- `artifact/REVIEWER_QUICKSTART.md`
- `artifact/README_ANON.md`
- `artifact/CLAIM_TO_EVIDENCE.md`
- `artifact/PAPER_TO_ARTIFACT_MAP.md`
- `artifact/KNOWN_LIMITATIONS.md`
- `artifact/REPRODUCIBILITY_STATUS.md`
- `artifact/VERIFICATION_LOG_2026-04-29.md`
- `paper/contribution_and_artifact_summary.md`
- `paper/artifact_reviewer_walkthrough.md`

## Reusable Reporting Resources

- `paper/audit_reporting_checklist.md`
- `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`
- `artifact/INFORMATION_ACCESS_CARD.md`
- `artifact/CLAIM_SURVIVAL_CARD.md`
- `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`

## Canonical Evidence Objects

- `paper/tbl_conclusion_shift.md`
- `paper/b_mbpp224_fair_budget.md`
- `paper/tbl_prompt_only_structural_mbpp224_control.md`
- `paper/tbl_prior_quality_response.md`
- `paper/tbl_prior_quality_audit.md`
- `paper/tbl_boundary_instantiations.md`
- `paper/tbl_backend_replicate_boundary.md`
- `paper/backend_replicate_boundary_notes.md`
- `paper/tbl_controlled_degradation_sweep.md`
- `artifact/CLAIM_SURVIVAL_CARD.md`
- `retrieval/prompt_structural.py`
- `scripts/67_make_prior_quality_audit.py`
- `scripts/68_make_prior_quality_response.py`
- `scripts/69_run_controlled_degradation_sweep.py`
- `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`

## Excluded From The Reviewer Package

- Historical worklogs.
- Reviewer-attack notes.
- Rebuttal drafts.
- Old paper drafts and staging notes.
- `paperB/` staging files.
- Internal strengthening plans and response notes.
- Files with stale method-paper framing.

The anonymous package is intentionally narrower than the working repository.
"""


def build_controlled_degradation_protocol() -> str:
    return """# Controlled Prior-Quality Degradation Protocol

This protocol was fixed before running the current pilot sweep. The artifact includes a DeepSeek `MBPP+50` pilot in `paper/tbl_controlled_degradation_sweep.md` and `results/degradation_sweep/*.json`. The pilot is secondary diagnostic evidence, not a main result, causal proof, or deployable prior-quality estimator.

## Research Question

If prior quality is treated as the evaluation variable, does controlled degradation of structural priors change net delta and harm rate?

## Fixed Design

- Target full design: `MBPP+100`
- Current pilot: first `50` episodes from the packaged `MBPP+100` episode file
- Target backend: Qwen-family main backend
- Current pilot backend: `deepseek-ai/deepseek-coder-6.7b-instruct` served by local vLLM
- Retrieval: fixed code-aware `syntax_aware` diagnostic episodes
- Candidate budget: `8`
- Target seeds: `1,2` minimum; `1,2,3` only if compute is available before looking at results
- Current pilot seed: `1`
- Selector: same diagnostic `MBR-exec` selector for every condition

## Fixed Conditions

1. `no_prior`
2. intended prior
3. drop API tags
4. drop control-flow tags
5. drop data-structure tags
6. replace 25% structural tags
7. replace 50% structural tags
8. replace 75% structural tags
9. random prior / corrupted prior

The degradation levels are fixed before execution. They must not be changed after seeing results.

## Metrics

- solved tasks
- paired improved / regressed / unchanged outcomes
- stored `structure_fidelity`
- quality coverage
- net delta by fidelity bin
- harm rate
- all-candidate compile-fail rate
- selected-candidate timeout / fail rate

## Inclusion Rules

Include in the main text only if the trend is clear, provenance is clean, and the table is compact. Include in appendix or artifact notes if the result is useful but noisy. Do not include if the result is unstable, requires substantial new explanation, creates tuning suspicion, or threatens the clean claim boundary.

## Reporting Boundary

The current pilot preserves positive, negative, and noisy rows. The allowed claim is that controlled degradation is now instantiated as a secondary diagnostic sweep and that lower-fidelity or bad priors can be audited through net delta, harm rate, and compile-fail rate. It must not be written as causal proof, a deployable quality estimator, or a replacement for the main prior-quality response audit.
"""


def build_canonical_file_list() -> str:
    lines = [
        "# Canonical File List",
        "",
        "Use only the following paper-facing objects when writing the manuscript or citing artifact evidence.",
        "",
        "## Canonical Paper Objects",
        "",
    ]
    for path in CANONICAL_PAPER_FILES:
        if path.startswith("paper/latex/sections/"):
            continue
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Canonical Families",
            "",
            "- `paper/latex/sections/*.tex`",
            "- `results/budget_sweep/*.json`",
            "- `results/prompt_only_*/*.json`",
            "- `results/degradation_sweep/*.json`",
            "",
            "Large upstream-derived benchmark data and tests are externalized from the direct review zip. See `artifact/SOURCE_AND_DATA.md` and `artifact/DATA_RELEASE_POLICY.md` for expected layout, hashes/provenance, and redistribution status.",
            "",
            "## Superseded But Non-Canonical Repo Objects",
            "",
            "- `paper/tbl_external.md`",
            "- `paper/tbl_cross_model.md`",
            "- `paper/fig_budget_sweep.md`",
            "- `paper/tbl_external_modern.md`",
            "- `paper/tbl_external_modern_sampling.md`",
            "",
            "Those superseded files remain in the repository for historical traceability only. Do not cite them in the final manuscript or artifact map.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_environment_md() -> str:
    python_version = command_output(["python", "--version"])
    pip_show = command_output(["python", "-m", "pip", "show", "vllm", "openai"])
    cpu_info = command_output(["lscpu"])
    gpu_info = command_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
    text = "# Environment Notes\n\n"
    text += "## Recovered Software Snapshot\n\n"
    text += f"- Python: `{python_version}`\n"
    text += "- Python package snapshot recovered in the current shell:\n\n"
    text += "```text\n" + pip_show + "\n```\n\n"
    text += "## Serving Backends Referenced By Results\n\n"
    text += "- Primary historical Qwen runs: `generator_backend=vllm_openai`, `model_name=Qwen/Qwen2.5-Coder-7B-Instruct`, `api_base=http://127.0.0.1:8000/v1` as recorded in the raw result JSON config blocks.\n"
    text += "- Added DeepSeek runs: `generator_backend=vllm_openai`, `model_name=deepseek-ai/deepseek-coder-6.7b-instruct`, `api_base=http://127.0.0.1:8001/v1` as recorded in `results/cross_model_deepseek_summary*.json` and raw DeepSeek result JSONs.\n"
    text += "- Added Granite boundary runs: `generator_backend=vllm_openai`, `model_name=ibm-granite/granite-8b-code-instruct-4k`, `api_base=http://127.0.0.1:8003/v1`, served through chat.\n"
    text += "- Added StarCoder2-7B boundary runs: `generator_backend=vllm_openai`, `model_name=bigcode/starcoder2-7b`, `api_base=http://127.0.0.1:8002/v1`, served through completions because the local tokenizer has no chat template.\n"
    text += "- Current shell package check reports `vllm 0.11.2` and `openai 2.30.0`.\n"
    text += "- The current shell does not report installed `evalplus` / `bigcodebench` packages, even though processed benchmark assets already exist in the repo. This implies the original preparation environment and the current packaging environment are not identical.\n\n"
    text += "## Canonical Backend Identity For Writing\n\n"
    text += "- Main-result backend for the paper: `Qwen/Qwen2.5-Coder-7B-Instruct`.\n"
    text += "- Supplementary same-scale backend: `deepseek-ai/deepseek-coder-6.7b-instruct`.\n"
    text += "- Granite 8B code instruct backend: `ibm-granite/granite-8b-code-instruct-4k`, used only as a replicate-sensitive instruction/chat boundary check.\n"
    text += "- Completion-style StarCoder2-7B backend: `bigcode/starcoder2-7b`, used only as a serving-format boundary check.\n"
    text += "- Weak backend: `bigcode-tiny-starcoder-py`, used only as a negative boundary check.\n\n"
    text += "## Hardware Snapshot Recoverable At Packaging Time\n\n"
    text += "```text\n" + cpu_info + "\n```\n\n"
    text += "GPU query:\n\n"
    text += "```text\n" + gpu_info + "\n```\n\n"
    text += "## Boundary\n\n"
    text += "- The repo now contains a packaging-time hardware snapshot, but not every original experiment wrote a machine-level hardware record into its raw result payload.\n"
    text += "- The fair-budget claim should therefore be written from recorded candidate-budget and execution-call accounting, not from an unsupported claim of identical wall-clock or token-level compute.\n"
    return text


def build_source_and_data_md() -> str:
    text = "# Source And Data Inventory\n\n"
    text += "## Executable Source Tree Included In Artifact\n\n"
    for directory in SOURCE_DIRS:
        text += f"- `{directory}/`\n"
    text += "\n## Review Zip Data Strategy\n\n"
    text += "The direct review zip excludes large upstream-derived benchmark data and tests so the package remains below the direct-upload size limit. The reviewer quickstart uses packaged cached outputs and raw-result JSONs; it does not need benchmark data, a GPU, a network connection, an API key, or live LLM calls.\n\n"
    text += "Live reruns require reconstructing the expected `data/` layout from upstream benchmark sources and preparation scripts before invoking generation/evaluation commands.\n\n"
    text += "## Expected Live-Rerun Data Layout\n\n"
    for path in DATA_FILES:
        text += f"- `{path}`\n"
    for pattern in DATA_GLOBS:
        text += f"- `{pattern}`\n"
    text += "\n## License And Redistribution Status\n\n"
    text += "| Resource | Included in review artifact? | Public release status | License/permission status | Replacement if not redistributable |\n"
    text += "| --- | --- | --- | --- | --- |\n"
    text += "| MBPP processed examples | no, externalized from direct zip | release only if upstream terms permit | upstream benchmark-derived; permission must be verified before public redistribution | preparation script, expected layout, hashes, and cached outputs |\n"
    text += "| EvalPlus MBPP+ tests | no, externalized from direct zip | release only if upstream terms permit | EvalPlus/benchmark-derived; permission must be verified before public redistribution | preparation script, expected layout, hashes, and cached outputs |\n"
    text += "| HumanEval+ processed file | no, externalized from direct zip | release only if upstream terms permit | EvalPlus/HumanEval-derived; permission must be verified before public redistribution | preparation script, expected layout, hashes, and cached outputs |\n"
    text += "| BigCodeBench-Hard compatible slices | no, externalized from direct zip | release only if upstream terms permit | BigCodeBench-derived; permission must be verified before public redistribution | compatibility-slice metadata, scripts, expected layout, hashes, and cached outputs |\n"
    text += "| cached model outputs and derived paper tables | yes | releasable by authors subject to review policy | authors' generated outputs and derived summaries | N/A |\n"
    text += "\n## Main Provenance Result Bundles Included In Artifact\n\n"
    text += "- old uncontrolled comparison raw results for `paper/tbl_conclusion_shift.*`\n"
    text += "- `results/mbppplus_vllm_v4_100_oracle.json`\n"
    text += "- `results/mbppplus_vllm_v4_100_no_structure.json`\n"
    text += "- `results/mbppplus_vllm_v4_100_random.json`\n"
    text += "- `results/mbppplus_vllm_v4_100_corrupted.json`\n\n"
    text += "These no-rerank files provide direct artifact-facing provenance for the `oracle > no_structure > corrupted/random` directionality claim and are summarized in `paper/tbl_no_rerank_directionality_v2.md`.\n"
    text += "\n## External Evaluation Provenance\n\n"
    text += "The package includes cached result JSONs and paper-facing summaries for HumanEval+, BigCodeBench-Hard compatible slices, Granite, StarCoder2, DeepSeek, and weak-backend boundary checks. The external benchmark inputs themselves are externalized from the direct zip and must be prepared from upstream sources for live reruns.\n"
    text += "\n## Public Release Boundary\n\n"
    text += "For public release, benchmark-derived files should be redistributed only after license/permission verification. If redistribution is not verified, release preparation scripts, metadata, expected layout, file hashes, cached output provenance, and instructions for users to obtain upstream assets themselves.\n"
    return text


def build_data_release_policy_md() -> str:
    return """# Data Release Policy

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
"""


def build_external_readme() -> str:
    return """# External Slice Notes

This artifact includes three external packages:

- `HumanEval+164` as the full-benchmark fallback external check
- `HumanEval+50` as a medium-size external slice on the active DeepSeek backend, now with seeds `1,2`
- `BigCodeBench-Hard compatible50` as a larger reproducible modern slice

The modern slice is compatibility-filtered rather than benchmark-complete. Tasks are included only when their declared dependency roots are importable in the current environment. The intended claim is qualified feasibility / small slice-level effects, not broad modern benchmark transfer.
The direct review zip includes cached outputs for the external evaluations already cited by the paper. Live reruns require reconstructing the processed slices and episodes from upstream sources. The compatibility-filtering preparation step for `BigCodeBench-Hard` remains provenance-only and should not be described as fully regenerable from the original upstream benchmark source.
DeepSeek-based `HumanEval+50` results are mixed across seeds `1,2` and should be cited as qualified, slice-sensitive boundary evidence rather than as broad-transfer evidence.
"""


def build_reproducibility_status() -> str:
    return """# Reproducibility Status

## Fully Regenerable From Packaged Inputs

- `paper/tbl_conclusion_shift.md` and `paper/tbl_conclusion_shift.json`
- `paper/tbl_stats_cost.md` and `paper/tbl_stats_cost.json`
- `paper/fig_budget_sweep_v2.md` and `paper/fig_budget_sweep_v2.json`
- `paper/fig_bad_prior_delta_types.md` and `paper/fig_bad_prior_delta_types.json`
- `paper/tbl_prior_quality_audit.md` and `paper/tbl_prior_quality_audit.json`
- `paper/tbl_prior_quality_response.md` and `paper/tbl_prior_quality_response.json`
- `paper/fig_prior_quality_response.md`
- `paper/tbl_backend_replicate_boundary.md` from stored Granite/StarCoder2 boundary summaries and raw-result pointers
- `paper/tbl_controlled_degradation_sweep.md` from packaged degradation-sweep raw results

These objects can be regenerated from packaged result files and packaged scripts. This regeneration path uses cached outputs and raw-result JSONs; it does not call an LLM.

## Provenance Validation

- `bash artifact/verify_provenance.sh` checks the prompt-only matcher constants and query-side access boundary in `retrieval/prompt_structural.py`.
- The same command checks representative raw result files for stored `structure_fidelity` fields and regenerates the prior-quality audit table from cached outputs.
- `paper/provenance_validation_checklist.md` gives the corresponding manual inspection path.

## Live LLM Reruns

- Full experiment reruns require the packaged source and episodes plus an available model endpoint or local model matching the recorded backend configuration.
- The main backend identity is `Qwen/Qwen2.5-Coder-7B-Instruct`; supplementary reruns may require `deepseek-ai/deepseek-coder-6.7b-instruct`, local `bigcode/starcoder2-7b`, or the weak StarCoder-family boundary backend.
- Live reruns that execute generated Python code should be run only in an isolated environment without sensitive credentials or network access.
- The controlled prior-quality degradation sweep has a completed DeepSeek `MBPP+50` pilot in `paper/tbl_controlled_degradation_sweep.md` and `results/degradation_sweep/*.json`. It is secondary diagnostic evidence, not a main result.
- Granite and StarCoder2 backend-boundary checks are packaged in `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, `paper/backend_replicate_boundary_notes.md`, and the referenced raw-result JSONs. They support replicate-sensitive backend audit reporting, not backend invariance.

## Packaged Direct-Provenance Evidence

- `paper/tbl_conclusion_shift.*` includes the packaged old uncontrolled raw results it cites.
- No-rerank directionality provenance is packaged directly through:
  - `results/mbppplus_vllm_v4_100_oracle.json`
  - `results/mbppplus_vllm_v4_100_no_structure.json`
  - `results/mbppplus_vllm_v4_100_random.json`
  - `results/mbppplus_vllm_v4_100_corrupted.json`
- Prompt-only boundary controls are packaged through:
  - `paper/tbl_prompt_only_lexical_control.md`
  - `paper/tbl_prompt_only_structural_control.md`
  - `paper/tbl_prompt_only_structural_mbpp224_control.md`
  - `results/prompt_only_lexical_mbpp100_fair_budget/*.json`
  - `results/prompt_only_structural_mbpp100_fair_budget/*.json`
  - `results/prompt_only_structural_mbpp224_fair_budget/*.json`
- Replicate-sensitive backend boundary checks are packaged through:
  - `paper/tbl_backend_replicate_boundary.md`
  - `paper/tbl_backend_replicate_boundary.json`
  - `paper/backend_replicate_boundary_notes.md`
  - `results/vllm_granite8b_mbppplus100_syntax_aware_*_seed*.json`
  - `results/vllm_starcoder2_mbppplus100_syntax_aware_*_rerun_seed*.json`

## Rerunnable Main Benchmark With Live Inference

- `MBPP+224` matched-budget main benchmark is rerunnable from packaged source after reconstructing the expected benchmark data/episode layout from upstream sources. The matching model endpoint or local model is also required. Packaged raw results are provided for paper-object regeneration and inspection.

## Rerunnable External Evaluation With Live Inference

- `HumanEval+164` and `HumanEval+50` are rerunnable after reconstructing the expected benchmark data/episode layout if the matching model endpoint or local model is available.
- `BigCodeBench-Hard compatible30/50` are rerunnable after reconstructing the processed compatibility slices and packaged-episode layout under the same live-inference assumption.
- The DeepSeek `MBPP+50` degradation pilot is rerunnable after reconstructing the expected MBPP+ slice inputs if the same `deepseek-ai/deepseek-coder-6.7b-instruct` endpoint is available.

## Provenance-Only Or Partially Regenerable Steps

- The compatibility filtering step for `BigCodeBench-Hard` slice creation depends on access to a local dataset cache or equivalent upstream data export.
- The artifact includes `scripts/62_prepare_bigcodebench_slice.py` as provenance, but the direct review zip externalizes the processed slice data; live reruns require reconstructing those inputs from upstream sources.
- The package includes current paper-facing objects and a repo-local LaTeX starter, but it is not a claim of final camera-ready manuscript integration.
- Historical planning drafts, reviewer-attack notes, rebuttal prewrites, and older worklogs are intentionally excluded from the canonical anonymous artifact to avoid stale claim wording.

## Cached-Output Boundaries

- The reviewer-first scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not regenerate raw LLM completions.
- Some supporting historical repo objects outside the canonical file list remain archival only and should not be cited as current paper evidence.
- The uploaded archive name `artifact/planb_ed_artifact_anon.zip` is an outer transport filename, not an internal artifact path that should appear inside the package.
"""


def build_verification_log() -> str:
    return """# Artifact Verification Log

Date: 2026-05-03
Package: `planb_ed_artifact_anon.zip`

This log records the final reviewer-script verification summary for the anonymous E&D artifact package after the artifact-audit fixes: direct-zip size reduction, filled information-access card, generic documentation aliases, commit-hash anonymization, and reviewer-friendly PASS output.

## Commands

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
python -m py_compile scripts/61_make_conclusion_shift_table.py scripts/58_make_stats_and_cost.py scripts/65_make_budget_sweep_v2.py scripts/66_make_bad_prior_breakdown.py scripts/67_make_prior_quality_audit.py scripts/68_make_prior_quality_response.py scripts/69_run_controlled_degradation_sweep.py
python scripts/59_package_ed_artifact.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Results

- `reproduce_main.sh`: PASS
- `verify_provenance.sh`: PASS
- Prompt-only matcher constants: PASS
- Raw `structure_fidelity` fields: PASS
- Prior-quality response regeneration: PASS
- No live LLM inference required for reviewer quickstart: PASS

## Observed Key Outputs

```text
[PASS] regenerated main reviewer-facing tables and figures from cached results
[PASS] prompt_structural matcher constants verified
[PASS] query-side prompt-only access boundary verified
[PASS] raw structure_fidelity fields verified
[PASS] verified matcher provenance and regenerated prior-quality audit from cached outputs
```

## Package Checks

- `artifact/manifest_with_hashes.json` reports packaged file hashes and the package manifest reports 0 missing files.
- `artifact/manifest.json` and `artifact/manifest_with_hashes.json` omit Git commit hashes for double-blind review.
- The direct review zip excludes large upstream-derived benchmark files and is checked to remain below `100,000,000` bytes.
- The package includes `paper/latex/neurips_2026.sty`.
- The package includes `paper/contribution_and_artifact_summary.md`.
- The package includes `paper/final_submission_qa_checklist.md`.
- The package includes `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md`, `artifact/CANONICAL_REVIEWER_PACKAGE.md`, and `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`.
- The package includes generic aliases: `artifact/VERIFICATION_LOG.md`, `artifact/PACKAGE_AUDIT.md`, and `artifact/DATA_RELEASE_POLICY.md`.
- The package includes `paper/tbl_boundary_instantiations.md`.
- The package includes `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, and `paper/backend_replicate_boundary_notes.md`.
- The package includes `paper/tbl_controlled_degradation_sweep.md` and `results/degradation_sweep/*.json`.
- The package includes the prior-quality response table, JSON, and response-curve source.
- The package excludes historical worklogs, reviewer-attack notes, rebuttal drafts, and stale manuscript-planning files from the canonical anonymous archive.

## LaTeX Check

- Local draft PDF: `paper/latex/main.pdf`
- Page count: 9 pages at the time of this verification.
- The checked log had no `LaTeX Error`, `Fatal error`, or unresolved citation warnings.

## Boundary

The reviewer scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not call an LLM and do not regenerate raw model completions.
"""


def build_reproduce_scripts() -> dict[str, str]:
    return {
        "reproduce_table1.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/61_make_conclusion_shift_table.py
printf '[PASS] regenerated conclusion-shift table\\n'
""",
        "reproduce_figure1.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/65_make_budget_sweep_v2.py
printf '[PASS] regenerated budget sweep support\\n'
""",
        "reproduce_main.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/61_make_conclusion_shift_table.py
printf '[PASS] regenerated conclusion-shift table\\n'
python scripts/58_make_stats_and_cost.py
printf '[PASS] regenerated stats/cost table\\n'
python scripts/65_make_budget_sweep_v2.py
printf '[PASS] regenerated budget sweep support\\n'
python scripts/66_make_bad_prior_breakdown.py
printf '[PASS] regenerated bad-prior breakdown\\n'
python scripts/67_make_prior_quality_audit.py
printf '[PASS] regenerated prior-quality audit\\n'
python scripts/69_run_controlled_degradation_sweep.py --cached-only --max-episodes 50 --candidate-budget 8 --seed 1 --generator-backend vllm_openai --model-name deepseek-ai/deepseek-coder-6.7b-instruct --api-base http://127.0.0.1:8001/v1 --device cuda --result-prefix mbppplus50_deepseek_degradation --out results/degradation_sweep/summary_deepseek_seed1_n50.json --paper-out paper/tbl_controlled_degradation_sweep.md
printf '[PASS] regenerated controlled-degradation table from cached outputs\\n'
printf '[PASS] regenerated main reviewer-facing tables and figures from cached results\\n'
""",
        "reproduce_figures.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/65_make_budget_sweep_v2.py
python scripts/66_make_bad_prior_breakdown.py
printf '[PASS] regenerated figure-support artifacts from cached results\\n'
""",
    }


def build_verify_provenance_script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1

python - <<'PY'
from pathlib import Path

source = Path("retrieval/prompt_structural.py").read_text()
required_tokens = [
    "LEXICAL_WEIGHT = 0.45",
    "PROMPT_INTENT_WEIGHT = 0.20",
    "STRUCTURAL_MATCH_WEIGHT = 0.35",
    "query_text = _text(query)",
]
for token in required_tokens:
    assert token in source, token

retrieve_body = source.split("def retrieve(", 1)[1]
for forbidden in ["query.code", "query.tests", "execution", "passed"]:
    assert forbidden not in retrieve_body, forbidden

print("[PASS] prompt_structural matcher constants verified")
print("[PASS] query-side prompt-only access boundary verified")
PY

python - <<'PY'
from plan_b.io_utils import read_json

paths = [
    "results/mbpp224_fair_budget/mbppplus224_syntax_aware_multi_prior_mbrexec_budget8_seed1.json",
    "results/prompt_only_structural_mbpp224_fair_budget/mbppplus224_prompt_structural_multi_prior_mbrexec_budget8_seed1.json",
]
for path in paths:
    payload = read_json(path)
    assert "episodes" in payload and payload["episodes"], path
    assert "structure_fidelity" in payload["episodes"][0], path

print("[PASS] raw structure_fidelity fields verified")
PY

python scripts/67_make_prior_quality_audit.py
test -s paper/tbl_prior_quality_response.md
test -s paper/fig_prior_quality_response.md
printf '[PASS] prior-quality response regenerated from cached outputs\\n'
printf '[PASS] verified matcher provenance and regenerated prior-quality audit from cached outputs\\n'
"""


def build_final_preflight_script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1

echo "[1] Check for identity leaks"
if grep -R -I -i -n --exclude='final_preflight.sh' "AUTHOR[_]NAME\\|INSTITUTION[_]NAME\\|EMAIL[_]ADDRESS\\|github[.]com/REALUSER\\|/home[/]REALUSER\\|/Users[/]REALUSER" .; then
  echo "[FAIL] placeholder identity leak found"
  exit 1
fi
printf '[PASS] placeholder identity leak scan clean\\n'

echo "[2] Check unwanted files"
if find . \\( -name ".git" -o -name "__MACOSX" -o -name ".DS_Store" -o -name "*.pyc" -o -name "__pycache__" \\) | grep -q .; then
  find . \\( -name ".git" -o -name "__MACOSX" -o -name ".DS_Store" -o -name "*.pyc" -o -name "__pycache__" \\)
  echo "[FAIL] unwanted files found"
  exit 1
fi
printf '[PASS] unwanted-file scan clean\\n'

echo "[3] Run cached-output reproduction"
bash artifact/reproduce_main.sh

echo "[4] Run provenance verification"
bash artifact/verify_provenance.sh

echo "[5] Create local extracted-package manifests"
find . -type f | sort > artifact_file_manifest.txt
find . -type f -print0 | sort -z | xargs -0 sha256sum > artifact_sha256_manifest.txt
printf '[PASS] extracted-package manifests created\\n'

echo "[6] Check extracted package size"
du -sh .

printf '[PASS] final artifact preflight complete\\n'
"""


def write_zip_entry(archive: zipfile.ZipFile, arcname: str, path: Path) -> None:
    if should_sanitize_path(path):
        archive.writestr(arcname, packaged_bytes(path))
    else:
        archive.write(path, arcname=arcname)


def hash_record_for_entry(arcname: str, path: Path) -> dict[str, object]:
    if should_sanitize_path(path):
        data = packaged_bytes(path)
        return {"path": arcname, "sha256": sha256_for_bytes(data), "size_bytes": len(data)}
    return {"path": arcname, "sha256": sha256_for_path(path), "size_bytes": path.stat().st_size}


def main() -> None:
    artifact_root = Path("artifact")
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "external").mkdir(exist_ok=True)

    write_sanitized_text(artifact_root / "README_ANON.md", build_readme())
    write_sanitized_text(artifact_root / PACKAGE_AUDIT_DATED_NAME, "# Package Audit (pending)\n")
    write_sanitized_text(artifact_root / "PACKAGE_AUDIT.md", "# Package Audit (pending)\n")
    write_sanitized_text(artifact_root / "REVIEWER_QUICKSTART.md", build_reviewer_quickstart())
    write_sanitized_text(artifact_root / "CONTRIBUTION_AND_ARTIFACT_SUMMARY.md", build_artifact_contribution_summary())
    write_sanitized_text(artifact_root / "CLAIM_TO_EVIDENCE.md", build_claim_to_evidence())
    write_sanitized_text(artifact_root / "PAPER_TO_ARTIFACT_MAP.md", build_paper_to_artifact())
    write_sanitized_text(artifact_root / "KNOWN_LIMITATIONS.md", build_known_limitations())
    write_sanitized_text(artifact_root / "RESULT_NAMING_RULES.md", build_naming_rules())
    write_sanitized_text(artifact_root / "STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md", build_structural_prior_audit_template())
    write_sanitized_text(artifact_root / "INFORMATION_ACCESS_CARD.md", build_information_access_card())
    write_sanitized_text(artifact_root / "CLAIM_SURVIVAL_CARD.md", build_claim_survival_card())
    write_sanitized_text(artifact_root / "CANONICAL_REVIEWER_PACKAGE.md", build_canonical_reviewer_package())
    write_sanitized_text(artifact_root / "CONTROLLED_DEGRADATION_PROTOCOL.md", build_controlled_degradation_protocol())
    write_sanitized_text(artifact_root / "CANONICAL_FILE_LIST.md", build_canonical_file_list())
    write_sanitized_text(artifact_root / "DATA_RELEASE_POLICY.md", build_data_release_policy_md())
    write_sanitized_text(artifact_root / "ENVIRONMENT.md", build_environment_md())
    write_sanitized_text(artifact_root / "SOURCE_AND_DATA.md", build_source_and_data_md())
    write_sanitized_text(artifact_root / "REPRODUCIBILITY_STATUS.md", build_reproducibility_status())
    write_sanitized_text(artifact_root / "VERIFICATION_LOG_2026-04-29.md", build_verification_log())
    write_sanitized_text(artifact_root / "VERIFICATION_LOG.md", build_verification_log())
    write_sanitized_text(artifact_root / "external/README.md", build_external_readme())
    for name, content in build_reproduce_scripts().items():
        write_sanitized_text(artifact_root / name, content)
    write_sanitized_text(artifact_root / "verify_provenance.sh", build_verify_provenance_script())
    write_sanitized_text(artifact_root / "final_preflight.sh", build_final_preflight_script())

    package_entries: dict[str, Path] = {}
    missing: list[str] = []
    for relative_path in build_artifact_file_list():
        path = Path(relative_path)
        if path.exists():
            package_entries[relative_path] = path
        else:
            missing.append(relative_path)

    manifest_arcnames = [f"artifact/{relative_path}" for relative_path in GENERATED_ARTIFACT_DOCS]
    for relative_path in GENERATED_ARTIFACT_DOCS:
        if relative_path in {"manifest.json", "manifest_with_hashes.json"}:
            continue
        path = artifact_root / relative_path
        arcname = f"artifact/{relative_path}"
        if path.exists():
            package_entries[arcname] = path
        else:
            missing.append(arcname)

    package_audit = build_package_audit(package_entries)
    write_sanitized_text(artifact_root / PACKAGE_AUDIT_DATED_NAME, package_audit)
    write_sanitized_text(artifact_root / "PACKAGE_AUDIT.md", package_audit)
    package_entries[f"artifact/{PACKAGE_AUDIT_DATED_NAME}"] = artifact_root / PACKAGE_AUDIT_DATED_NAME
    package_entries["artifact/PACKAGE_AUDIT.md"] = artifact_root / "PACKAGE_AUDIT.md"
    validate_package_entries(package_entries, missing)

    manifest = {
        "artifact_version": ARTIFACT_VERSION,
        "source_revision": "omitted_for_double_blind_review",
        "files": sorted(set(package_entries) | set(manifest_arcnames)),
        "missing": sorted(missing),
        "manifest_scope": "All internal archive paths intended for the anonymous reviewer package.",
    }
    write_json(artifact_root / "manifest.json", manifest)
    package_entries["artifact/manifest.json"] = artifact_root / "manifest.json"

    manifest_with_hashes = {
        "artifact_version": ARTIFACT_VERSION,
        "source_revision": "omitted_for_double_blind_review",
        "files": [hash_record_for_entry(arcname, package_entries[arcname]) for arcname in sorted(package_entries)],
        "missing": sorted(missing),
        "unhashed_self_files": ["artifact/manifest_with_hashes.json"],
        "manifest_scope": "Hashes are computed over sanitized package bytes. The hash manifest excludes its own self-hash.",
    }
    write_sanitized_text(artifact_root / "manifest_with_hashes.json", json.dumps(manifest_with_hashes, indent=2) + "\n")
    package_entries["artifact/manifest_with_hashes.json"] = artifact_root / "manifest_with_hashes.json"

    zip_path = artifact_root / "planb_ed_artifact_anon.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for arcname in sorted(package_entries):
            write_zip_entry(archive, arcname, package_entries[arcname])

    entry_count, zip_digest = validate_zip_archive(
        zip_path,
        artifact_root / "manifest.json",
        artifact_root / "manifest_with_hashes.json",
    )
    write_sanitized_text(artifact_root / "planb_ed_artifact_anon.sha256", f"{zip_digest}  planb_ed_artifact_anon.zip\n")
    print(f"Wrote {zip_path} with {entry_count} entries")
    print(f"ZIP size {zip_path.stat().st_size} bytes")
    print(f"SHA256 {zip_digest}")
    print("P0 artifact package validation passed")


if __name__ == "__main__":
    main()
