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
ARTIFACT_VERSION = "anonymous-review-2026-05-06"
PACKAGE_AUDIT_DATED_NAME = "PACKAGE_AUDIT_2026-05-06.md"
DIRECT_ZIP_SIZE_LIMIT_BYTES = 100_000_000

CANONICAL_PAPER_FILES = [
    "README.md",
    "requirements.txt",
    "requirements-review.txt",
    "requirements-live.txt",
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
    "neurips2026_ed_latex_source_FINAL_v2/README_SOURCE.md",
    "neurips2026_ed_latex_source_FINAL_v2/paper.tex",
    "neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex",
    "neurips2026_ed_latex_source_FINAL_v2/references.bib",
    "neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty",
    "neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png",
    "neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.pdf",
]

PAPER_GLOBS: list[str] = []

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
    "REVIEWER_WORKFLOW.md",
    "PROJECT_GUIDE_FOR_REVIEWERS.md",
    "OUTPUT_INTERPRETATION_GUIDE.md",
    "LIVE_RERUN_GUIDE.md",
    "FULL_REPRODUCTION_GUIDE.md",
    "EXPERIMENT_RERUN_GUIDE.md",
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
    "reviewer_audit.sh",
    "run_smoke_test.sh",
    "check_live_rerun_prereqs.sh",
    "verify_provenance.sh",
    "final_preflight.sh",
    "VERIFICATION_LOG_2026-05-06.md",
    "VERIFICATION_LOG.md",
    "manifest.json",
    "manifest_with_hashes.json",
]

P0_REQUIRED_PACKAGE_PATHS = [
    "README.md",
    "requirements.txt",
    "requirements-review.txt",
    "requirements-live.txt",
    "artifact/README_ANON.md",
    "artifact/REVIEWER_QUICKSTART.md",
    "artifact/REVIEWER_WORKFLOW.md",
    "artifact/PROJECT_GUIDE_FOR_REVIEWERS.md",
    "artifact/OUTPUT_INTERPRETATION_GUIDE.md",
    "artifact/LIVE_RERUN_GUIDE.md",
    "artifact/FULL_REPRODUCTION_GUIDE.md",
    "artifact/EXPERIMENT_RERUN_GUIDE.md",
    "artifact/CONTRIBUTION_AND_ARTIFACT_SUMMARY.md",
    "artifact/reviewer_audit.sh",
    "artifact/run_smoke_test.sh",
    "artifact/check_live_rerun_prereqs.sh",
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
    "artifact/VERIFICATION_LOG_2026-05-06.md",
    "artifact/VERIFICATION_LOG.md",
    "artifact/PACKAGE_AUDIT_2026-05-06.md",
    "artifact/PACKAGE_AUDIT.md",
    "artifact/DATA_RELEASE_POLICY.md",
    "artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md",
    "artifact/INFORMATION_ACCESS_CARD.md",
    "artifact/CLAIM_SURVIVAL_CARD.md",
    "artifact/CONTROLLED_DEGRADATION_PROTOCOL.md",
    "neurips2026_ed_latex_source_FINAL_v2/README_SOURCE.md",
    "neurips2026_ed_latex_source_FINAL_v2/paper.tex",
    "neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex",
    "neurips2026_ed_latex_source_FINAL_v2/references.bib",
    "neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty",
    "neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png",
    "neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.pdf",
    "paper/tbl_prior_quality_response.md",
    "paper/tbl_prior_quality_response.json",
    "paper/prompt_only_structural_matcher.md",
    "retrieval/prompt_structural.py",
    "paper/tbl_backend_replicate_boundary.md",
    "paper/tbl_backend_replicate_boundary.json",
    "paper/backend_replicate_boundary_notes.md",
    "paper/tbl_controlled_degradation_sweep.md",
    "scripts/69_run_controlled_degradation_sweep.py",
    "scripts/70_reviewer_claim_audit.py",
    "scripts/71_run_pipeline_smoke_test.py",
    "scripts/72_check_live_rerun_prereqs.py",
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
        "# Package Audit (2026-05-06)",
        "",
        "This file is generated by `scripts/59_package_ed_artifact.py`. The packaging script fails before writing the final archive if any P0 required file is missing or if stale internal files are included.",
        "",
        "The direct review zip externalizes large upstream-derived benchmark files so the archive can stay below the 100MB direct-upload threshold. Reviewer quickstart commands use packaged cached outputs and do not require those externalized benchmark files.",
        "",
        "The final archive SHA256 is written after zip creation to the sidecar file `artifact/planb_ed_artifact_anon.sha256`. The archive hash is not embedded inside the archive itself because doing so would make the zip hash self-referential.",
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
            "bash artifact/reviewer_audit.sh",
            "bash artifact/reproduce_main.sh",
            "bash artifact/verify_provenance.sh",
            "```",
            "",
            "## Default Script Stability",
            "",
            "- `artifact/reproduce_main.sh` uses `python -S` through a safe Python runner and wraps each Python regeneration step with a 90-second timeout when GNU/coreutils `timeout` is available.",
            "- `artifact/verify_provenance.sh` uses the same `python -S` runner for inline provenance checks and prior-quality regeneration.",
            "- `artifact/run_smoke_test.sh` uses `python -S` and a 60-second timeout when available.",
            "- The scripts set `PYTHONNOUSERSITE=1` and `PYTHONPATH` to the extracted package root to avoid user-site startup hooks while keeping local project modules importable.",
            "",
            "## Final Preflight Behavior",
            "",
            "- `bash artifact/final_preflight.sh` is intended to be idempotent inside an extracted copy.",
            "- It removes and rewrites its extracted-package manifests on each run.",
            "- It excludes those generated manifest files from the manifest content so a second run does not create self-referential diffs.",
            "- It runs the optional smoke test under `timeout` when that command is available.",
            "",
            "## Upload Guidance",
            "",
            "- Main paper PDF for review should be uploaded through OpenReview separately.",
            "- Authoritative final LaTeX source package in this artifact: `neurips2026_ed_latex_source_FINAL_v2/paper.tex`.",
            "- Anonymous artifact archive: `artifact/planb_ed_artifact_anon.zip`.",
            "- Archive SHA256 sidecar: `artifact/planb_ed_artifact_anon.sha256`.",
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
    text = "# SPC-Audit Anonymous Artifact\n\n"
    text += "## What This Artifact Is\n\n"
    text += f"This package accompanies the NeurIPS 2026 E&D submission \"{FINAL_PAPER_TITLE}\". The paper studies structural-prior evaluation as an evaluation-design problem: after matching candidate budget, accounting for execution calls, disclosing information access, separating diagnostic from deployable selection, and auditing prior quality, which structural-prior claim remains warranted?\n\n"
    text += "This package is both a complete experimental codebase for the structural-prior evaluation pipeline and a reviewer-fast claim-audit/provenance package for checking the paper's evidence path. It contains code for episode construction, retrieval and prior construction, candidate generation, diagnostic execution-based selection, evaluation, table construction, cached-output regeneration, and provenance verification.\n\n"
    text += "The contribution is SPC-Audit, a reviewer-inspectable reporting pattern and claim-audited artifact. It is not a deployable code-generation system, new benchmark, leaderboard submission, broad-transfer result, backend-invariance result, strongest-method claim, or deployment-safety claim.\n\n"
    text += "## Start Here\n\n"
    text += "Run these commands from the extracted artifact root:\n\n"
    text += "```bash\n"
    text += "cat artifact/REVIEWER_WORKFLOW.md\n"
    text += "bash artifact/reviewer_audit.sh\n"
    text += "bash artifact/reproduce_main.sh\n"
    text += "bash artifact/verify_provenance.sh\n"
    text += "```\n\n"
    text += "`reviewer_audit.sh` is the main reviewer-facing verifier: it prints the headline numbers, where they came from, how they were recomputed, and what claim each number does or does not support. `reproduce_main.sh` then regenerates paper-facing tables from packaged cached outputs, and `verify_provenance.sh` checks prompt-only matcher / prior-quality provenance. These three commands do not call an LLM, require a GPU, require an API key, require network access, or execute generated code.\n\n"
    text += "## If You Only Have 10 Minutes\n\n"
    text += "Run:\n\n"
    text += "```bash\n"
    text += "bash artifact/reviewer_audit.sh\n"
    text += "bash artifact/reproduce_main.sh\n"
    text += "bash artifact/verify_provenance.sh\n"
    text += "```\n\n"
    text += "These commands verify the paper-facing claim-to-evidence path from cached outputs. They do not call an LLM, do not require GPU/API keys/network, and do not execute generated code.\n\n"
    text += "After running them, check:\n\n"
    text += "- main matched-budget result: `178.67 -> 185.00`;\n"
    text += "- paired directionality: `30 improved` vs. `11 regressed`;\n"
    text += "- prompt-only boundary: full MBPP+224 prompt-only rerun is non-positive;\n"
    text += "- quality response: medium/high fidelity net `+17`, low fidelity net `+2`;\n"
    text += "- provenance checks: prompt-only query-side access boundary and stored `structure_fidelity`.\n\n"
    text += "## What Do The PASS Messages Mean?\n\n"
    text += "The PASS messages mean that the artifact can regenerate and verify the derived paper-facing evidence from packaged cached outputs. They do not mean that all LLM generations were rerun. The default reviewer path checks table regeneration, prompt-only matcher constants, query-side prompt-only access boundaries, stored `structure_fidelity` fields, prior-quality audit regeneration, and claim-to-evidence consistency.\n\n"
    text += "## Full Experiment Rerun At A Glance\n\n"
    text += "The quickstart above verifies the paper claims from packaged raw-result JSONs. To regenerate raw model outputs and rerun the full main experiment, start with:\n\n"
    text += "```bash\n"
    text += "cat artifact/FULL_REPRODUCTION_GUIDE.md\n"
    text += "bash artifact/check_live_rerun_prereqs.sh\n"
    text += "```\n\n"
    text += "The full live rerun requires preparing MBPP/EvalPlus-derived data under `data/`, building the episode files, starting a Qwen OpenAI-compatible endpoint at `http://127.0.0.1:8000/v1`, then running `scripts/51_run_mbpp224_fair_budget.py` with the matched-budget settings in the guide. This path calls an LLM and executes generated Python code, so it should be run in Linux/WSL/container-style isolation rather than as the default reviewer quickstart.\n\n"
    text += "## Important Windows Smoke-Test Note\n\n"
    text += "Python's `resource` module is Unix-only. This artifact treats it as optional: Linux/WSL/macOS use POSIX resource limits, while Windows smoke tests use `subprocess` timeout. On Windows, run:\n\n"
    text += "```bash\n"
    text += "python scripts/71_run_pipeline_smoke_test.py\n"
    text += "```\n\n"
    text += "If a stale artifact copy reports `ModuleNotFoundError: No module named 'resource'`, it is an environment-compatibility bug in that stale copy, not a paper-result failure. Use the updated package or the direct Python smoke-test entry point above.\n\n"
    text += "## What The Paper Claims\n\n"
    text += "- C0: the older `167/224 -> 184/224` comparison is an operational pipeline gain, but it is entangled and not attributed to the structural prior alone.\n"
    text += "- C1: the supported positive result is a scoped fixed code-aware diagnostic effect on `MBPP+224`: `no_prior + MBR = 178.67 +/- 0.58` and `multi_prior + MBR = 185.00 +/- 1.73`.\n"
    text += "- C2: the main scientific finding is quality-conditioned evaluation: intended code-aware priors show most positive movement in medium/high retrospective-fidelity bins, while low-quality or misleading priors can shrink or reverse gains.\n"
    text += "- C3: full `MBPP+224` prompt-only structural retrieval is not supported: `no_prior = 179.33 +/- 2.31`, `multi_prior = 177.67 +/- 1.53`.\n"
    text += "- C4: broad transfer, backend invariance, strongest-method performance, deployment-time `MBR-exec`, causal mechanism proof, and deployable prior-quality estimation are explicit non-claims.\n\n"
    text += "The authoritative final LaTeX source edited by the expert is in `neurips2026_ed_latex_source_FINAL_v2/paper.tex`; the OpenReview paper PDF should be uploaded separately. This artifact includes the final source, checklist, figure asset, NeurIPS style file, and the paper-facing evidence objects that support the claims.\n\n"
    text += "## Final Paper Object Map\n\n"
    text += "| Final paper object | Artifact support |\n"
    text += "| --- | --- |\n"
    text += "| Figure 1: claim-audit logic | `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png` |\n"
    text += "| Table 1: claim audit card | `artifact/CLAIM_SURVIVAL_CARD.md`, `paper/claim_matrix_v2.md` |\n"
    text += "| Table 2: SPC-Audit checklist | `paper/audit_reporting_checklist.md`, `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md` |\n"
    text += "| Table 3: main MBPP+224 matched-budget result | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json` |\n"
    text += "| Table 4: prior-quality response | `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json` |\n"
    text += "| Table 5: prompt-only boundary controls | `paper/tbl_prompt_only_structural_mbpp224_control.md` |\n"
    text += "| Table 6: compact boundary instantiations | `paper/tbl_boundary_instantiations.md` |\n\n"
    text += "The authoritative paper for review is the PDF uploaded to OpenReview. The final LaTeX source package in `neurips2026_ed_latex_source_FINAL_v2/` is provided for artifact-paper mapping; stale draft PDFs under older paths are intentionally excluded from the review zip.\n\n"
    text += "## Main Evidence Map\n\n"
    text += "| Reviewer question | Where to look |\n"
    text += "| --- | --- |\n"
    text += "| What is the final paper source? | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `checklist_filled.tex`, `figure1_claim_audit_logic.*` |\n"
    text += "| What claims are supported or unsupported? | `artifact/CLAIM_TO_EVIDENCE.md`, `artifact/CLAIM_SURVIVAL_CARD.md`, `artifact/KNOWN_LIMITATIONS.md` |\n"
    text += "| Can I verify the paper's exact numeric claims quickly? | `artifact/reviewer_audit.sh`, `scripts/70_reviewer_claim_audit.py` |\n"
    text += "| Can paper-facing tables be regenerated? | `artifact/reproduce_main.sh`, `scripts/61_make_conclusion_shift_table.py`, `scripts/58_make_stats_and_cost.py`, `scripts/67_make_prior_quality_audit.py` |\n"
    text += "| Is prompt-only matching query-prompt-only on the query side? | `artifact/verify_provenance.sh`, `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |\n"
    text += "| Does the prior-quality audit read stored fields rather than tune retrieval? | `artifact/verify_provenance.sh`, `paper/prior_quality_audit_provenance.md`, `paper/tbl_prior_quality_response.md` |\n"
    text += "| Where are the raw-result files for the main table? | `results/mbpp224_fair_budget/*.json`, `results/mbpp224_fair_budget/summary.json` |\n"
    text += "| Where are prompt-only boundary outputs? | `results/prompt_only_structural_mbpp224_fair_budget/*.json`, `paper/tbl_prompt_only_structural_mbpp224_control.md` |\n"
    text += "| Where are external/backend boundary outputs? | `paper/tbl_boundary_instantiations.md`, `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` |\n"
    text += "| Can I run any project code end-to-end locally? | `artifact/run_smoke_test.sh`, `scripts/71_run_pipeline_smoke_test.py` |\n"
    text += "| What requires live LLM inference and full data/model setup? | `artifact/FULL_REPRODUCTION_GUIDE.md`, `artifact/check_live_rerun_prereqs.sh`, `artifact/REPRODUCIBILITY_STATUS.md`, `artifact/SOURCE_AND_DATA.md`, `artifact/ENVIRONMENT.md` |\n\n"
    text += "## Recommended Reading Order\n\n"
    text += "1. `artifact/REVIEWER_QUICKSTART.md`\n"
    text += "2. `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`\n"
    text += "3. `artifact/OUTPUT_INTERPRETATION_GUIDE.md`\n"
    text += "4. `artifact/CLAIM_TO_EVIDENCE.md`\n"
    text += "5. `artifact/KNOWN_LIMITATIONS.md`\n"
    text += "6. `artifact/LIVE_RERUN_GUIDE.md`\n\n"
    text += "For deeper inspection, start with `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`.\n\n"
    text += "## Code And Reproduction Modes\n\n"
    text += "The artifact includes the complete executable project source tree used by the paper-facing scripts: `plan_b/`, `generation/`, `retrieval/`, `structure/`, `gating/`, `rerank/`, `guardrails/`, `eval/`, `verifier/`, `scripts/`, and `configs/`.\n\n"
    text += "There are three reproduction modes:\n\n"
    text += "1. Reviewer quickstart / cached-output regeneration: regenerates derived paper objects from packaged result JSONs. This is the default path for artifact review and requires only Python plus packaged repo modules.\n"
    text += "2. Local pipeline smoke test: `bash artifact/run_smoke_test.sh` builds a one-task synthetic dataset and runs the real pipeline with the non-LLM `retrieval_edit` backend. It proves that the project code path executes, but it is not paper evidence.\n"
    text += "3. Live experiment reruns: rebuild raw generations and execute generated code on MBPP+/HumanEval+/BigCodeBench-style inputs. This requires upstream benchmark assets, matching model endpoints or local models, optional GPU infrastructure, and an isolated execution environment. Start with `artifact/FULL_REPRODUCTION_GUIDE.md`, then run `bash artifact/check_live_rerun_prereqs.sh` to see exactly which data files, optional Python modules, and local endpoints are still missing.\n\n"
    text += "Large upstream-derived benchmark data and tests are externalized from the direct review zip because the local `data/` tree is multi-GB and includes benchmark-derived assets whose redistribution requires upstream permission checks. The package instead includes cached outputs, raw-result JSONs, preparation scripts, expected layouts, provenance notes, and hashes/manifests for review.\n\n"
    text += "## Canonical Evidence Objects\n\n"
    text += "- Final paper source: `neurips2026_ed_latex_source_FINAL_v2/paper.tex`\n"
    text += "- Main fair-budget table: `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json`\n"
    text += "- Conclusion-shift table: `paper/tbl_conclusion_shift.md`, `paper/tbl_conclusion_shift.json`\n"
    text += "- Stats/cost and paired directionality: `paper/tbl_stats_cost.md`, `paper/tbl_task_clustered_paired_stats.md`\n"
    text += "- Prompt-only boundary controls: `paper/tbl_prompt_only_lexical_control.md`, `paper/tbl_prompt_only_structural_control.md`, `paper/tbl_prompt_only_structural_mbpp224_control.md`\n"
    text += "- Prior-quality response: `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`\n"
    text += "- Bad-prior harm decomposition: `paper/fig_bad_prior_delta_types.md`, `paper/bad_prior_failure_breakdown.md`\n"
    text += "- Boundary instantiations: `paper/tbl_boundary_instantiations.md`, `paper/tbl_external_v2.md`, `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md`\n"
    text += "- Reusable audit resources: `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md`\n"
    text += "- Package integrity: `artifact/manifest.json`, `artifact/manifest_with_hashes.json`, `artifact/PACKAGE_AUDIT.md`; the transport zip SHA256 is provided as the sidecar file `artifact/planb_ed_artifact_anon.sha256` next to the zip, not inside the zip.\n\n"
    text += "## Safety And Data Release\n\n"
    text += "Generated Python code is untrusted. The reviewer quickstart does not execute generated code. Live reruns that execute generated programs should be run only in an appropriate sandbox without sensitive credentials or network access.\n\n"
    text += "Public release follows `artifact/DATA_RELEASE_POLICY.md`: upstream benchmark datasets or tests are redistributed only when permission is verified. Otherwise the release should provide preparation scripts, metadata, expected directory layout, hashes, and cached-output provenance.\n"
    return text

def build_artifact_contribution_summary() -> str:
    return """# Contribution And Artifact Summary

This reviewer-facing note summarizes the submission contribution and the artifact entry points. The paper is an evaluation-design and artifact contribution, not a new structural-prior method, new benchmark, leaderboard package, or broad-transfer claim.

## Contribution Position

The central contribution is **SPC-Audit**, a prior-quality-aware diagnostic audit protocol for structural-prior claims in execution-evaluated code generation. The main scientific finding is quality-conditioned evaluation: an average prior-vs-no-prior delta is insufficient unless the evaluation also reports prior-quality coverage, net movement by quality band, harm rate, and which claims survive the audit.

The reusable pattern has five parts:

1. **Fair-budget diagnostic audit.** Compare prior conditions under matched candidate budget and matched execution-call accounting, while explicitly disclosing information access and selection status.
2. **Information-access boundary controls.** Separate fixed code-aware diagnostic evidence from prompt-only controls and oracle-derived stress tests.
3. **Prior-quality response audit.** Report quality coverage, bin-level net delta, harm rate, outcome-level fidelity separation, and threshold sensitivity instead of only average prior-versus-no-prior solved-task deltas.
4. **Claim survival hierarchy.** Label operational, diagnostic, prompt-only, quality-conditioned, and broad-transfer claims by what assumptions they survive.
5. **Boundary reporting and explicit non-claims.** External/backend rows, budget sweeps, and controlled-degradation pilots are used to define scope; they are not broad-transfer, backend-invariance, robustness, or deployment claims.

## Reviewer Entry Points

| Reviewer Question | Artifact Entry Point |
| --- | --- |
| What is the expert-edited final paper source? | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex` |
| Which claims are supported, qualified, or unsupported? | `artifact/CLAIM_TO_EVIDENCE.md`, `artifact/KNOWN_LIMITATIONS.md` |
| Can the paper-facing tables be regenerated without live LLM inference? | `artifact/reproduce_main.sh` |
| Is the prompt-only structural matcher fixed and query-prompt-only on the query side? | `artifact/verify_provenance.sh`, `paper/prompt_only_structural_matcher.md`, `retrieval/prompt_structural.py` |
| Does the prior-quality response audit read stored raw-result fields rather than tuning retrieval or filtering episodes? | `artifact/verify_provenance.sh`, `paper/prior_quality_audit_provenance.md`, `scripts/67_make_prior_quality_audit.py` |
| What requires live model inference rather than cached-output regeneration? | `artifact/FULL_REPRODUCTION_GUIDE.md`, `artifact/check_live_rerun_prereqs.sh`, `artifact/REPRODUCIBILITY_STATUS.md` |
| How can another project reuse the reporting pattern? | `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`, `artifact/INFORMATION_ACCESS_CARD.md`, `artifact/CLAIM_SURVIVAL_CARD.md` |
| Where are small boundary instantiations outside the main table summarized? | `paper/tbl_boundary_instantiations.md` |
| Where are backend-sensitive boundary checks summarized? | `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` |
| Where is the secondary controlled-degradation pilot? | `paper/tbl_controlled_degradation_sweep.md`, `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md` |

## Claim Boundary

The artifact supports scoped positive claims about conclusion shift, fixed code-aware diagnostic gains, prompt-only boundaries, quality-conditioned evaluation, bad-prior harm, and boundary reporting. It does not support a strongest-method claim, deployable prompt-only structural-prior method, deployment-time `MBR-exec` selector, backend invariance, broad transfer, clean StarCoder2 instruction-backend replication, causal mechanism proof from `structure_fidelity`, deployable prior-quality estimation, or a new benchmark claim.

## Quickstart

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```
"""


def build_reviewer_quickstart() -> str:
    return """# Reviewer Quickstart

Run from the artifact root:

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

## Requirements for quickstart

- GPU: not required
- API key: not required
- LLM endpoint: not required
- Network: not required
- Executes generated code: no
- Expected runtime: about 1 minute on a standard CPU environment
- Python dependencies: standard library plus packaged repository modules; see `requirements-review.txt`

## Important Windows Smoke-Test Note

Python's `resource` module is Unix-only. The current artifact makes it optional in `rerank/sandbox_runner.py`: Linux/WSL/macOS use POSIX resource limits, while Windows smoke tests use subprocess timeout.

On Windows without `bash`, run:

```bash
python scripts/71_run_pipeline_smoke_test.py
```

If you see `ModuleNotFoundError: No module named 'resource'`, you are using a stale artifact copy. That error is an environment-compatibility issue in the stale copy, not evidence that the paper results cannot be audited.

## What each command answers

| Command | Reviewer question answered |
| --- | --- |
| `bash artifact/reviewer_audit.sh` | Do the raw packaged JSONs actually contain the headline paper numbers, paired directionality, prompt-only boundary, and prior-quality response? |
| `bash artifact/reproduce_main.sh` | Can the paper-facing tables be regenerated from cached outputs rather than hand-written? |
| `bash artifact/verify_provenance.sh` | Is the prompt-only matcher fixed/query-prompt-only, and does the prior-quality audit read stored fields? |
| `bash artifact/run_smoke_test.sh` | Optional: does the real pipeline code execute end-to-end on a local toy fixture? This runs generated toy code and is not part of the default no-execution quickstart. |

## Expected output

The audit script prints the actual numbers before the final PASS line. You should see lines like:

```text
[PASS] reviewer claim audit matched the paper's headline numbers and boundaries
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

No live LLM inference is required for the default quickstart.

## Runtime table

| Command | Expected runtime | Requires GPU? | Calls LLM? | Executes generated code? |
| --- | ---: | --- | --- | --- |
| `bash artifact/reviewer_audit.sh` | ~10 sec | no | no | no |
| `bash artifact/reproduce_main.sh` | ~30 sec | no | no | no |
| `bash artifact/verify_provenance.sh` | ~20 sec | no | no | no |
| `bash artifact/run_smoke_test.sh` | ~10 sec | no | no | yes, toy fixture only |
| live reruns | hours/days | yes/endpoint | yes | yes |

Start with:

1. `artifact/REVIEWER_WORKFLOW.md`
2. `artifact/PROJECT_GUIDE_FOR_REVIEWERS.md`
3. `artifact/OUTPUT_INTERPRETATION_GUIDE.md`
4. `artifact/README_ANON.md`
5. `artifact/CLAIM_TO_EVIDENCE.md`
6. `artifact/KNOWN_LIMITATIONS.md`
7. `artifact/LIVE_RERUN_GUIDE.md`

## Troubleshooting

- If Python cannot import local modules, run from the artifact root.
- If cached outputs are missing, verify archive extraction completed.
- If live rerun scripts are invoked accidentally, stop and use the three default quickstart scripts only.
- If a shell reports permission issues for scripts, invoke them with `bash path/to/script.sh`.
- On Windows without `bash`, run the smoke test directly with `python scripts/71_run_pipeline_smoke_test.py` from the artifact root.
"""


def build_project_guide_for_reviewers() -> str:
    return """# Project Guide for Reviewers

## Purpose

This artifact is a complete experimental codebase plus a reviewer-fast provenance package for the paper. The codebase implements the evaluation pipeline used to construct episodes, generate candidates, retrieve priors, apply diagnostic `MBR-exec` selection, evaluate generated programs, and regenerate paper-facing tables.

## Pipeline Overview

1. Episode construction creates query/support/test records.
2. Retrieval constructs code-aware and prompt-only conditions.
3. Prior construction produces single, multi, random, or corrupted priors.
4. Candidate generation produces candidate programs.
5. Diagnostic `MBR-exec` selects candidates using packaged tests.
6. Evaluation records pass/fail outcomes.
7. Table builders regenerate paper-facing summaries from cached outputs.
8. Provenance checks verify information-access and prior-quality boundaries.

## Full Codebase Directory Map

| Directory | Reviewer meaning |
| --- | --- |
| `configs/` | experiment configuration files |
| `plan_b/` | core pipeline, schemas, and I/O utilities |
| `generation/` | candidate generation and prompt construction utilities |
| `retrieval/` | lexical, syntax-aware, and prompt-only retrieval utilities |
| `structure/` | structure extraction and prior support utilities |
| `gating/` | prior/gating support code |
| `rerank/` | diagnostic `MBR-exec` selection and sandbox runner |
| `guardrails/` | guardrail helpers used by the pipeline |
| `eval/` | execution-based evaluation utilities |
| `verifier/` | static and learned verifier utilities |
| `scripts/` | experiment runners and table/audit builders |
| `results/` | cached outputs and summaries used for paper-facing regeneration |
| `paper/` | derived paper-facing tables and figure-support files |
| `artifact/` | reviewer-facing guides, scripts, claim maps, and provenance checks |

## What Is Canonical Evidence?

The canonical evidence for the paper is listed in `artifact/CLAIM_TO_EVIDENCE.md` and summarized in `artifact/PAPER_TO_ARTIFACT_MAP.md`. Exploratory files should not be used as main-claim evidence unless they are explicitly listed there.

## Reviewer-Fast Path

Use:

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

This path checks the paper-facing evidence from cached outputs. It does not call an LLM, require GPU/API/network access, or execute untrusted generated code.

## Optional Live Path

Live reruns are documented in `artifact/LIVE_RERUN_GUIDE.md` and `artifact/FULL_REPRODUCTION_GUIDE.md`. They require external assets, model endpoints, and sandboxed execution, and are not needed for the default reviewer audit.
"""


def build_output_interpretation_guide() -> str:
    return """# Output Interpretation Guide

## What Does `reviewer_audit.sh` Show?

It prints the paper's main claim-to-evidence chain in human-readable form:

- uncontrolled operational gain;
- matched-budget diagnostic result;
- paired directionality;
- prompt-only boundary;
- prior-quality response;
- bad-prior and boundary non-claims.

The script recomputes the reported values from packaged JSON files before printing the final PASS line.

## What Does `reproduce_main.sh` Prove?

It regenerates derived paper-facing tables from cached outputs. It proves that the reported paper tables are reconstructible from the packaged cached results. It does not rerun LLM generation.

## What Does `verify_provenance.sh` Prove?

It verifies prompt-only matcher constants, query-side access boundaries, stored `structure_fidelity` fields, and prior-quality audit regeneration.

## What Do PASS Messages Not Mean?

They do not mean:

- full live LLM reruns were performed;
- the system is deployable;
- `MBR-exec` is a deployment-time reranker;
- `structure_fidelity` is a deployable estimator;
- broad transfer or backend invariance is supported;
- all model-serving nondeterminism has been eliminated.

## How To Read The Main Numbers

| Reviewer-visible output | Paper interpretation |
| --- | --- |
| `178.67 -> 185.00` | scoped matched-budget code-aware diagnostic effect on `MBPP+224` |
| `30 improved / 11 regressed / 631 unchanged` | positive paired directionality, not a robustness claim |
| prompt-only `179.33` vs `177.67` | full prompt-only structural rerun is non-positive |
| medium/high net `+17` vs low net `+2` | prior quality conditions the observed effect |
| random/corrupted priors below baseline | misleading priors can harm under the same diagnostic selector |
"""


def build_live_rerun_guide() -> str:
    return """# Live Rerun Guide

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
"""


def build_reviewer_workflow() -> str:
    return """# Reviewer Workflow

This guide is organized around the three questions an E&D artifact reviewer is likely to ask.

## 1. What is this project and what is the contribution?

Read:

```bash
cat README.md
cat artifact/PROJECT_GUIDE_FOR_REVIEWERS.md
cat artifact/CLAIM_TO_EVIDENCE.md
cat artifact/KNOWN_LIMITATIONS.md
```

Short answer: SPC-Audit is a diagnostic reporting pattern for structural-prior claims in execution-evaluated code generation. The main claim is quality-conditioned evaluation: a structural prior should not be evaluated only by average prior-vs-no-prior delta; reviewers should also see prior-quality coverage, quality-conditioned net delta, harm rate, information access, selector status, and explicit non-claims.

The expert-edited paper source is:

```text
neurips2026_ed_latex_source_FINAL_v2/paper.tex
```

## 2. Can I quickly verify the paper's numeric claims?

Run:

```bash
bash artifact/reviewer_audit.sh
```

This is the most important reviewer command. It reads packaged raw-result JSONs and checks:

- main fair-budget result: `178.67 -> 185.00`;
- paired query-seed directionality: `30 improved / 11 regressed`;
- task-clustered sensitivity: `14 positive / 5 negative / 205 zero`;
- full prompt-only structural boundary: `179.33` vs `177.67`;
- prior-quality response: medium/high `multi_prior` coverage `0.469`, `23 improved / 6 regressed / net +17`;
- bad-prior harm: random net `-19`, corrupted net `-16`;
- explicit non-claims.

Unlike a plain PASS-only script, this command prints the numbers and their interpretation before asserting them.

## 3. Can I regenerate paper-facing artifacts?

Run:

```bash
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

`reproduce_main.sh` regenerates derived tables from cached results. `verify_provenance.sh` checks that the prompt-only structural matcher uses only query prompt / entry point on the query side and that the prior-quality audit reads stored `structure_fidelity` fields.

For interpretation of PASS messages and non-claims, read:

```bash
cat artifact/OUTPUT_INTERPRETATION_GUIDE.md
```

## 4. Can I run project code locally?

Optional smoke test:

```bash
bash artifact/run_smoke_test.sh
```

This builds a one-task synthetic fixture and runs the real pipeline twice with the non-LLM `retrieval_edit` backend. It proves the code path executes locally. It is not paper evidence.

## 5. Can I rerun the real experiments?

Read:

```bash
cat artifact/LIVE_RERUN_GUIDE.md
cat artifact/FULL_REPRODUCTION_GUIDE.md
cat artifact/SOURCE_AND_DATA.md
cat artifact/ENVIRONMENT.md
bash artifact/check_live_rerun_prereqs.sh
```

Full live reruns require upstream benchmark assets and matching model endpoints or local models. They are not part of the default quickstart because they call LLMs and execute generated Python code.
"""


def build_full_reproduction_guide() -> str:
    return """# Full Reproduction Guide

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
python scripts/51_run_mbpp224_fair_budget.py \\
  --dataset mbppplus224 \\
  --retrieval syntax_aware \\
  --settings no_prior,multi_prior \\
  --budget 1 \\
  --seeds 1 \\
  --max-episodes 2 \\
  --generator-backend vllm_openai \\
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \\
  --api-base http://127.0.0.1:8000/v1 \\
  --device cpu \\
  --out /tmp/planb_qwen_live_sanity/summary.json \\
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
python scripts/03_prepare_evalplus.py \\
  --mbppplus-path data/raw/evalplus/MbppPlus.jsonl.gz \\
  --humanevalplus-path data/raw/evalplus/HumanEvalPlus.jsonl.gz \\
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
python scripts/01_build_episodes.py \\
  --train-path data/processed/mbpp/train.jsonl \\
  --eval-path data/processed/evalplus/mbppplus_test.jsonl \\
  --output-path data/episodes/mbppplus_test224_episodes.jsonl \\
  --shots 1 \\
  --retrieval-modes syntax_aware \\
  --limit-eval 224
```

Prompt-only structural boundary episodes:

```bash
python scripts/01_build_episodes.py \\
  --train-path data/processed/mbpp/train.jsonl \\
  --eval-path data/processed/evalplus/mbppplus_test.jsonl \\
  --output-path data/episodes/mbppplus_test224_prompt_structural_episodes.jsonl \\
  --shots 1 \\
  --retrieval-modes prompt_structural \\
  --limit-eval 224
```

MBPP+100 support episodes for boundary checks:

```bash
python scripts/01_build_episodes.py \\
  --train-path data/processed/mbpp/train.jsonl \\
  --eval-path data/processed/evalplus/mbppplus_test.jsonl \\
  --output-path data/episodes/mbppplus_test100_episodes.jsonl \\
  --shots 1 \\
  --retrieval-modes syntax_aware \\
  --limit-eval 100
```

HumanEval+50 syntax episodes:

```bash
python scripts/01_build_episodes.py \\
  --train-path data/processed/mbpp/train.jsonl \\
  --eval-path data/processed/evalplus/humanevalplus_test.jsonl \\
  --output-path data/episodes/humanevalplus_test50_syntax_episodes.jsonl \\
  --shots 1 \\
  --retrieval-modes syntax_aware \\
  --limit-eval 50
```

### 4.4 BigCodeBench-Hard Compatible Slices

BigCodeBench-Hard requires a local upstream Arrow export or dataset cache. Set:

```bash
export BIGCODEBENCH_HARD_ARROW=data/upstream/bigcodebench-hard-v0.1.4.arrow
```

Then prepare a compatibility-filtered slice:

```bash
python scripts/62_prepare_bigcodebench_slice.py \\
  --max-tasks 50 \\
  --source-arrow "$BIGCODEBENCH_HARD_ARROW" \\
  --out-examples data/processed/bigcodebench_hard_compatible50.jsonl \\
  --out-episodes data/episodes/bigcodebench_hard_compatible50_syntax_episodes.jsonl \\
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
python -m vllm.entrypoints.openai.api_server \\
  --model Qwen/Qwen2.5-Coder-7B-Instruct \\
  --served-model-name Qwen/Qwen2.5-Coder-7B-Instruct \\
  --host 127.0.0.1 \\
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
python scripts/51_run_mbpp224_fair_budget.py \\
  --dataset mbppplus224 \\
  --retrieval syntax_aware \\
  --settings no_prior,multi_prior \\
  --budget 8 \\
  --seeds 1 \\
  --max-episodes 20 \\
  --generator-backend vllm_openai \\
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \\
  --api-base http://127.0.0.1:8000/v1 \\
  --device cuda \\
  --out results/live_rerun_smoke/summary.json \\
  --paper-out paper/live_rerun_smoke.md
```

This confirms that data loading, retrieval, live generation, and `MBR-exec` execution are working. It is not the paper headline result.

## 7. Run The Full MBPP+224 Main Table

Use a separate output directory first, so the packaged audit files remain intact:

```bash
python scripts/51_run_mbpp224_fair_budget.py \\
  --dataset mbppplus224 \\
  --retrieval syntax_aware \\
  --settings no_prior,single_prior,multi_prior,random_prior,corrupted_prior \\
  --budget 8 \\
  --seeds 1,2,3 \\
  --all-settings-use-all-seeds \\
  --generator-backend vllm_openai \\
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \\
  --api-base http://127.0.0.1:8000/v1 \\
  --device cuda \\
  --out results/live_mbpp224_fair_budget/summary.json \\
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
python scripts/51_run_mbpp224_fair_budget.py \\
  --dataset mbppplus224 \\
  --retrieval prompt_structural \\
  --settings no_prior,single_prior,multi_prior \\
  --budget 8 \\
  --seeds 1,2,3 \\
  --episodes-path data/episodes/mbppplus_test224_prompt_structural_episodes.jsonl \\
  --generator-backend vllm_openai \\
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \\
  --api-base http://127.0.0.1:8000/v1 \\
  --device cuda \\
  --out results/live_prompt_only_structural_mbpp224/summary.json \\
  --paper-out paper/live_prompt_only_structural_mbpp224.md
```

This is the live counterpart of the full prompt-only boundary result in the paper.

## 10. Rerun External / Backend Boundary Checks

HumanEval+50 DeepSeek shape:

```bash
python scripts/55_run_external_slice.py \\
  --dataset humanevalplus50 \\
  --settings no_prior,multi_prior \\
  --candidate-budget 8 \\
  --seed 1 \\
  --generator-backend vllm_openai \\
  --model-name deepseek-ai/deepseek-coder-6.7b-instruct \\
  --api-base http://127.0.0.1:8001/v1 \\
  --result-prefix live_humanevalplus50_deepseek \\
  --out results/live_external_slice_humanevalplus50_deepseek_seed1.json \\
  --paper-out paper/live_external_slice_humanevalplus50_deepseek_seed1.md
```

BigCodeBench-Hard compatible slice shape:

```bash
python scripts/63_run_bigcodebench_slice.py \\
  --settings no_prior,multi_prior \\
  --candidate-budget 8 \\
  --seed 1 \\
  --generator-backend vllm_openai \\
  --model-name deepseek-ai/deepseek-coder-6.7b-instruct \\
  --api-base http://127.0.0.1:8001/v1 \\
  --eval-examples data/processed/bigcodebench_hard_compatible50.jsonl \\
  --episodes data/episodes/bigcodebench_hard_compatible50_syntax_episodes.jsonl \\
  --slice-tag bigcodebench_hard_compatible50 \\
  --max-episodes 50 \\
  --result-prefix live_bigcodebench_hard_compatible50 \\
  --out results/live_external_slice_bigcodebench_hard50_seed1.json \\
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
"""


def build_experiment_rerun_guide() -> str:
    return """# Experiment Rerun Guide

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
python scripts/51_run_mbpp224_fair_budget.py \\
  --dataset mbppplus224 \\
  --retrieval syntax_aware \\
  --settings no_prior,single_prior,multi_prior,random_prior,corrupted_prior \\
  --budget 8 \\
  --seeds 1,2,3 \\
  --all-settings-use-all-seeds \\
  --generator-backend vllm_openai \\
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \\
  --api-base http://127.0.0.1:8000/v1 \\
  --device cuda \\
  --out results/mbpp224_fair_budget/summary.json \\
  --paper-out paper/b_mbpp224_fair_budget.md
```

Boundary: this command calls a live model and executes generated Python code. Run it only in an isolated environment with resource limits. Exact bit-for-bit equality is not guaranteed across model serving stacks, but the protocol, budgets, seeds, settings, and result paths are fixed.

## Level 5: Focused Live Reruns

For a cheaper live rerun, use a subset:

```bash
python scripts/51_run_mbpp224_fair_budget.py \\
  --dataset mbppplus224 \\
  --retrieval syntax_aware \\
  --settings no_prior,multi_prior \\
  --budget 8 \\
  --seeds 1 \\
  --max-episodes 20 \\
  --generator-backend vllm_openai \\
  --model-name Qwen/Qwen2.5-Coder-7B-Instruct \\
  --api-base http://127.0.0.1:8000/v1 \\
  --device cuda \\
  --out results/live_rerun_smoke/summary.json \\
  --paper-out paper/live_rerun_smoke.md
```

This does not reproduce the headline table, but it exercises the same live-inference path on a smaller slice.

## External And Backend Boundary Reruns

HumanEval+ / external slice shape:

```bash
python scripts/55_run_external_slice.py \\
  --dataset humanevalplus50 \\
  --settings no_prior,multi_prior \\
  --candidate-budget 8 \\
  --seed 1 \\
  --generator-backend vllm_openai \\
  --model-name deepseek-ai/deepseek-coder-6.7b-instruct \\
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
"""


def build_claim_to_evidence() -> str:
    return """# Claim To Evidence Map

| ID | Claim | Status | Evidence | Boundary |
| --- | --- | --- | --- | --- |
| C0 | operational pipeline gain | supported operationally | `paper/tbl_conclusion_shift.md`, old uncontrolled raw results | Entangles structural conditioning and selection opportunity; not an attributed structural-prior claim. |
| C1 | matched-budget code-aware diagnostic effect | supported with scope | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json`, `paper/tbl_stats_cost.md`, `paper/tbl_task_clustered_paired_stats.md` | Fixed code-aware `syntax_aware` episodes, matched candidate budget and execution-call accounting, diagnostic `MBR-exec`. |
| C2 | quality-conditioned evaluation claim: prior presence alone is insufficient; intended code-aware priors show most positive movement in medium/high retrospective-fidelity bins; prompt-only high-fidelity coverage is rare; misleading priors can harm | supported diagnostic audit | `paper/tbl_prior_quality_audit.md`, `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json`, `paper/fig_prior_quality_response.md`, `paper/prior_quality_audit_provenance.md`, `results/mbpp224_fair_budget/summary.json`, `results/prompt_only_structural_mbpp224_fair_budget/summary.json`, `paper/fig_bad_prior_delta_types.md`, `paper/bad_prior_failure_breakdown.md` | Retrospective/reference-code-based; not a causal mechanism, scalar quality proof, or deployable quality estimator. |
| C3 | full prompt-only structural retrieval effect | not supported | `paper/tbl_prompt_only_structural_mbpp224_control.md`, `results/prompt_only_structural_mbpp224_fair_budget/summary.json` | Deployable prompt-only structural-prior claim is unsupported by the full `MBPP+224` rerun. |
| C4 | broad transfer / backend invariance / strongest-method claim | unsupported | `paper/tbl_external_v2.md`, `paper/tbl_boundary_instantiations.md`, `paper/tbl_cross_model_v2.md`, `paper/tbl_backend_replicate_boundary.md`, `paper/backend_replicate_boundary_notes.md` | External and backend rows are boundary instantiations; positive, neutral, mixed, and negative rows are retained. |
| Artifact | SPC-Audit is a reusable diagnostic audit protocol for structural-prior claims | supported artifact contribution | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `paper/audit_reporting_checklist.md`, `paper/contribution_and_artifact_summary.md`, `paper/claim_matrix_v2.md`, `paper/artifact_reviewer_walkthrough.md`, `artifact/PAPER_TO_ARTIFACT_MAP.md`, `artifact/CLAIM_SURVIVAL_CARD.md`, `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md` | Reporting pattern, not a new benchmark or deployable generation method. |
| Artifact | the audit filters claims by the assumptions they survive | supported | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `artifact/CLAIM_SURVIVAL_CARD.md` | Negative and boundary rows are part of the contribution. |
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

## Final Paper Object Numbering

| Final paper object | Artifact support |
| --- | --- |
| Figure 1: claim-audit logic | `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.pdf` |
| Table 1: claim audit card and survival hierarchy | `artifact/CLAIM_SURVIVAL_CARD.md`, `paper/claim_matrix_v2.md` |
| Table 2: SPC-Audit reporting checklist | `paper/audit_reporting_checklist.md`, `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md` |
| Table 3: main MBPP+224 matched-budget result | `paper/b_mbpp224_fair_budget.md`, `results/mbpp224_fair_budget/summary.json` |
| Table 4: prior-quality response card | `paper/tbl_prior_quality_response.md`, `paper/tbl_prior_quality_response.json` |
| Table 5: prompt-only boundary controls | `paper/tbl_prompt_only_structural_mbpp224_control.md`, `results/prompt_only_structural_mbpp224_fair_budget/summary.json` |
| Table 6: compact boundary instantiations | `paper/tbl_boundary_instantiations.md` |

The authoritative paper for review is the PDF uploaded to OpenReview. The final LaTeX source package here is provided for artifact-paper mapping; stale draft PDFs under older paths are intentionally excluded from the review zip.

| Paper Object | Artifact Location |
| --- | --- |
| expert-edited final paper source | `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`, `neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty` |
| one-page reviewer quickstart | `artifact/REVIEWER_QUICKSTART.md` |
| reviewer workflow and explanatory audit | `artifact/REVIEWER_WORKFLOW.md`, `artifact/reviewer_audit.sh`, `scripts/70_reviewer_claim_audit.py` |
| live rerun and smoke-test guide | `artifact/LIVE_RERUN_GUIDE.md`, `artifact/FULL_REPRODUCTION_GUIDE.md`, `artifact/check_live_rerun_prereqs.sh`, `artifact/EXPERIMENT_RERUN_GUIDE.md`, `artifact/run_smoke_test.sh`, `scripts/71_run_pipeline_smoke_test.py`, `scripts/72_check_live_rerun_prereqs.py` |
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
| latest verification log | `artifact/VERIFICATION_LOG.md`, `artifact/VERIFICATION_LOG_2026-05-06.md` |
| budget sweep with uncertainty | `paper/fig_budget_sweep_v2.md`, `paper/fig_budget_sweep_v2.json`, `results/budget_sweep/*.json` |
| no-rerank directionality provenance | `paper/tbl_no_rerank_directionality_v2.md`, `results/mbppplus_vllm_v4_100_oracle.json`, `results/mbppplus_vllm_v4_100_no_structure.json`, `results/mbppplus_vllm_v4_100_random.json`, `results/mbppplus_vllm_v4_100_corrupted.json` |
| external evidence table | `paper/tbl_external_v2.md`, `paper/external_protocol.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed1.md`, `paper/b_external_slice_humanevalplus50_deepseek_seed2.md`, `paper/tbl_external_modern50_deepseek.md` |
| cross-model table | `paper/tbl_cross_model_v2.md`, `paper/tbl_cross_model_v2.json`, `paper/tbl_cross_model_deepseek_two_seed.md`, `paper/tbl_cross_model_deepseek_two_seed.json`, `paper/tbl_cross_model_starcoder2_two_seed.md`, `paper/tbl_cross_model_starcoder2_two_seed.json` |
| boundary instantiations | `paper/tbl_boundary_instantiations.md` |
| replicate-sensitive backend boundary checks | `paper/tbl_backend_replicate_boundary.md`, `paper/tbl_backend_replicate_boundary.json`, `paper/backend_replicate_boundary_notes.md` |
| bad-prior harm decomposition | `paper/fig_bad_prior_delta_types.md`, `paper/fig_bad_prior_delta_types.json`, `paper/bad_prior_failure_breakdown.md` |
| concept figure support | `paper/figure1_concept.md`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`, `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.pdf` |
| final LaTeX source package | `neurips2026_ed_latex_source_FINAL_v2/README_SOURCE.md`, `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex`, `neurips2026_ed_latex_source_FINAL_v2/references.bib`, `neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty` |
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
- The package includes the expert-edited final LaTeX source package in `neurips2026_ed_latex_source_FINAL_v2/`, including the NeurIPS style file, filled checklist, and claim-audit figure asset. The OpenReview submission PDF should be uploaded separately.
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
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
```

## First Files To Inspect

- `artifact/REVIEWER_WORKFLOW.md`
- `artifact/REVIEWER_QUICKSTART.md`
- `artifact/README_ANON.md`
- `neurips2026_ed_latex_source_FINAL_v2/paper.tex`
- `artifact/CLAIM_TO_EVIDENCE.md`
- `artifact/PAPER_TO_ARTIFACT_MAP.md`
- `artifact/KNOWN_LIMITATIONS.md`
- `artifact/REPRODUCIBILITY_STATUS.md`
- `artifact/VERIFICATION_LOG_2026-05-06.md`
- `paper/contribution_and_artifact_summary.md`
- `paper/artifact_reviewer_walkthrough.md`

## Reusable Reporting Resources

- `paper/audit_reporting_checklist.md`
- `artifact/STRUCTURAL_PRIOR_AUDIT_TEMPLATE.md`
- `artifact/INFORMATION_ACCESS_CARD.md`
- `artifact/CLAIM_SURVIVAL_CARD.md`
- `artifact/CONTROLLED_DEGRADATION_PROTOCOL.md`

## Canonical Evidence Objects

- `neurips2026_ed_latex_source_FINAL_v2/paper.tex`
- `neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex`
- `neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png`
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
- `scripts/70_reviewer_claim_audit.py`
- `scripts/71_run_pipeline_smoke_test.py`
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
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Canonical Families",
            "",
            "- `results/budget_sweep/*.json`",
            "- `results/prompt_only_*/*.json`",
            "- `results/degradation_sweep/*.json`",
            "",
            "The authoritative final manuscript source is `neurips2026_ed_latex_source_FINAL_v2/paper.tex`. Older repo-local `paper/latex/` draft files are not part of the canonical reviewer package.",
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
    text += "## Important Reviewer Note\n\n"
    text += "The reviewer quickstart does not require GPU, model endpoints, API keys, network access, or generated-code execution. The GPU/model-serving details below document optional full live rerun conditions only.\n\n"
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
    text += "Live reruns require reconstructing the expected `data/` layout from upstream benchmark sources and preparation scripts before invoking generation/evaluation commands. The canonical step-by-step procedure is `artifact/FULL_REPRODUCTION_GUIDE.md`; run `bash artifact/check_live_rerun_prereqs.sh` to see which data files, optional modules, and local endpoints are still missing in a fresh extracted copy.\n\n"
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

- Expert-edited final manuscript source is packaged at `neurips2026_ed_latex_source_FINAL_v2/paper.tex`; the OpenReview PDF should be uploaded separately from this artifact.
- `bash artifact/reviewer_audit.sh` recomputes and verifies headline claim numbers from packaged raw-result JSONs.
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

- `bash artifact/run_smoke_test.sh` is a local code-path smoke test using a synthetic one-task fixture and the non-LLM `retrieval_edit` backend. It is not paper evidence.
- The primary live-rerun guide is `artifact/FULL_REPRODUCTION_GUIDE.md`; `bash artifact/check_live_rerun_prereqs.sh` reports the required review files, live data files, optional Python modules, and optional `/v1/models` endpoints.
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
- The package includes current paper-facing objects and the expert-edited final LaTeX source package. Reviewer quickstart does not depend on local LaTeX compilation; compiling the source requires a complete TeX installation with the NeurIPS style dependencies and fonts.
- Historical planning drafts, reviewer-attack notes, rebuttal prewrites, and older worklogs are intentionally excluded from the canonical anonymous artifact to avoid stale claim wording.

## Cached-Output Boundaries

- The reviewer-first scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not regenerate raw LLM completions.
- Some supporting historical repo objects outside the canonical file list remain archival only and should not be cited as current paper evidence.
- The uploaded archive name `artifact/planb_ed_artifact_anon.zip` is an outer transport filename, not an internal artifact path that should appear inside the package.
"""


def build_verification_log() -> str:
    return """# Artifact Verification Log

Date: 2026-05-06
Package: `planb_ed_artifact_anon.zip`
Archive SHA256: written after zip creation to sidecar file `artifact/planb_ed_artifact_anon.sha256`; the zip hash is not embedded inside the archive to avoid self-referential hash churn.

This log records the reviewer-script verification summary for the anonymous E&D artifact package after syncing the artifact to the expert-edited final paper source in `neurips2026_ed_latex_source_FINAL_v2/`.

## Commands

```bash
bash artifact/reviewer_audit.sh
bash artifact/reproduce_main.sh
bash artifact/verify_provenance.sh
bash artifact/check_live_rerun_prereqs.sh
bash artifact/check_live_rerun_prereqs.sh --check-endpoints
bash artifact/run_smoke_test.sh
python -m py_compile scripts/61_make_conclusion_shift_table.py scripts/58_make_stats_and_cost.py scripts/65_make_budget_sweep_v2.py scripts/66_make_bad_prior_breakdown.py scripts/67_make_prior_quality_audit.py scripts/68_make_prior_quality_response.py scripts/69_run_controlled_degradation_sweep.py scripts/70_reviewer_claim_audit.py scripts/71_run_pipeline_smoke_test.py scripts/72_check_live_rerun_prereqs.py
python scripts/01_build_episodes.py --help
python scripts/03_prepare_evalplus.py --help
python scripts/51_run_mbpp224_fair_budget.py --help
python scripts/55_run_external_slice.py --help
python scripts/62_prepare_bigcodebench_slice.py --help
python scripts/63_run_bigcodebench_slice.py --help
python scripts/51_run_mbpp224_fair_budget.py --dataset mbppplus224 --retrieval syntax_aware --settings no_prior,multi_prior --budget 2 --seeds 1 --max-episodes 3 --generator-backend retrieval_edit --device cpu --out /tmp/planb_mbpp_live_path_sanity/summary.json --paper-out /tmp/planb_mbpp_live_path_sanity/summary.md
CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server --model <HF_CACHE>/hub/models--Qwen--Qwen2.5-Coder-7B-Instruct/snapshots/c03e6d358207e414f1eca0bb1891e29f1db0e242 --served-model-name Qwen/Qwen2.5-Coder-7B-Instruct --host 127.0.0.1 --port 8000 --gpu-memory-utilization 0.50 --max-model-len 4096 --trust-remote-code
python scripts/72_check_live_rerun_prereqs.py --check-endpoints
python scripts/51_run_mbpp224_fair_budget.py --dataset mbppplus224 --retrieval syntax_aware --settings no_prior,multi_prior --budget 1 --seeds 1 --max-episodes 2 --generator-backend vllm_openai --model-name Qwen/Qwen2.5-Coder-7B-Instruct --api-base http://127.0.0.1:8000/v1 --device cpu --out /tmp/planb_qwen_live_sanity/summary.json --paper-out /tmp/planb_qwen_live_sanity/summary.md
python scripts/59_package_ed_artifact.py
PATH=<PROJECT_ROOT>/.texlive/2026/bin/x86_64-linux:$PATH latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
```

## Results

- `reviewer_audit.sh`: PASS
- `reproduce_main.sh`: PASS with `python -S` safe runner and per-step timeout wrapper
- `verify_provenance.sh`: PASS with `python -S` safe runner for inline checks and script calls
- `check_live_rerun_prereqs.sh`: PASS as a diagnostic report; expected missing live data/modules/endpoints do not block cached-output review
- `check_live_rerun_prereqs.sh --check-endpoints` before starting a local Qwen server: diagnostic completed; default reviewer files/data/modules were present, while local model endpoints were not reachable
- temporary Qwen vLLM endpoint at `127.0.0.1:8000`: PASS; `/v1/models` returned `Qwen/Qwen2.5-Coder-7B-Instruct`
- `check_live_rerun_prereqs.sh --check-endpoints` after starting Qwen: PASS for Qwen main endpoint; DeepSeek/StarCoder2/Granite boundary endpoints remained optional-live-missing
- `run_smoke_test.sh`: PASS in the packaging environment with `python -S` and timeout wrapper
- live-rerun script interface check: PASS for `scripts/01_build_episodes.py`, `scripts/03_prepare_evalplus.py`, `scripts/51_run_mbpp224_fair_budget.py`, `scripts/55_run_external_slice.py`, `scripts/62_prepare_bigcodebench_slice.py`, and `scripts/63_run_bigcodebench_slice.py`
- MBPP+224 real-data live-path sanity check with non-LLM `retrieval_edit`: PASS for data loading, episode loading, pipeline execution, sandboxed candidate execution, and output writing; not used as paper evidence
- MBPP+224 tiny Qwen live sanity check: PASS for endpoint integration, chat-completion generation, sandboxed evaluation, and output writing on 2 episodes with `settings=no_prior,multi_prior`, `budget=1`, `seed=1`; not used as paper evidence
- Prompt-only matcher constants: PASS
- Raw `structure_fidelity` fields: PASS
- Prior-quality response regeneration: PASS
- No live LLM inference required for reviewer quickstart: PASS
- Full raw LLM regeneration: NOT RUN; only the tiny Qwen sanity check was executed, not the full multi-seed, full-task rerun or the boundary endpoint reruns

## Observed Key Outputs

```text
[PASS] reviewer claim audit matched the paper's headline numbers and boundaries
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
- The package includes the expert-edited final paper source package: `neurips2026_ed_latex_source_FINAL_v2/paper.tex`, filled checklist, NeurIPS style file, and claim-audit figure assets.
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

- Authoritative final source: `neurips2026_ed_latex_source_FINAL_v2/paper.tex`.
- The OpenReview paper PDF should be uploaded separately from this artifact.
- In the current packaging shell, LaTeX compilation is blocked by an incomplete local TeX font/style installation. The artifact quickstart does not depend on LaTeX compilation.

## Boundary

The reviewer scripts regenerate derived paper objects from cached outputs and raw-result JSONs. They do not call an LLM and do not regenerate raw model completions.
"""


def build_reproduce_scripts() -> dict[str, str]:
    return {
        "reviewer_audit.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" -S scripts/70_reviewer_claim_audit.py
""",
        "run_smoke_test.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
if command -v timeout >/dev/null 2>&1; then
  timeout 60 "$PYTHON_BIN" -S scripts/71_run_pipeline_smoke_test.py
else
  echo "[WARN] timeout command not found; running smoke test without timeout"
  "$PYTHON_BIN" -S scripts/71_run_pipeline_smoke_test.py
fi
""",
        "check_live_rerun_prereqs.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python scripts/72_check_live_rerun_prereqs.py "$@"
""",
        "reproduce_table1.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" -S scripts/61_make_conclusion_shift_table.py
printf '[PASS] regenerated conclusion-shift table\\n'
""",
        "reproduce_figure1.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" -S scripts/65_make_budget_sweep_v2.py
printf '[PASS] regenerated budget sweep support\\n'
""",
        "reproduce_main.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
PYTHON_SAFE=("$PYTHON_BIN" "-S")

run_py() {
  local seconds="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" "${PYTHON_SAFE[@]}" "$@"
  else
    echo "[WARN] timeout command not found; running without timeout: $*"
    "${PYTHON_SAFE[@]}" "$@"
  fi
}

run_py 90 scripts/61_make_conclusion_shift_table.py
printf '[PASS] regenerated conclusion-shift table\\n'
run_py 90 scripts/58_make_stats_and_cost.py
printf '[PASS] regenerated stats/cost table\\n'
run_py 90 scripts/65_make_budget_sweep_v2.py
printf '[PASS] regenerated budget sweep support\\n'
run_py 90 scripts/66_make_bad_prior_breakdown.py
printf '[PASS] regenerated bad-prior breakdown\\n'
run_py 90 scripts/67_make_prior_quality_audit.py
printf '[PASS] regenerated prior-quality audit\\n'
run_py 90 scripts/69_run_controlled_degradation_sweep.py --cached-only --max-episodes 50 --candidate-budget 8 --seed 1 --generator-backend vllm_openai --model-name deepseek-ai/deepseek-coder-6.7b-instruct --api-base http://127.0.0.1:8001/v1 --device cuda --result-prefix mbppplus50_deepseek_degradation --out results/degradation_sweep/summary_deepseek_seed1_n50.json --paper-out paper/tbl_controlled_degradation_sweep.md
printf '[PASS] regenerated controlled-degradation table from cached outputs\\n'
printf '[PASS] regenerated main reviewer-facing tables and figures from cached results\\n'
""",
        "reproduce_figures.sh": """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" -S scripts/65_make_budget_sweep_v2.py
"$PYTHON_BIN" -S scripts/66_make_bad_prior_breakdown.py
printf '[PASS] regenerated figure-support artifacts from cached results\\n'
""",
    }


def build_verify_provenance_script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD"
PYTHON_BIN="${PYTHON:-python}"
PYTHON_SAFE=("$PYTHON_BIN" "-S")

"${PYTHON_SAFE[@]}" - <<'PY'
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

"${PYTHON_SAFE[@]}" - <<'PY'
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

"${PYTHON_SAFE[@]}" scripts/67_make_prior_quality_audit.py
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

echo "[3] Check final manuscript source package"
test -s neurips2026_ed_latex_source_FINAL_v2/paper.tex
test -s neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex
test -s neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty
test -s neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png
printf '[PASS] final manuscript source package present\\n'

echo "[4] Check live-rerun prerequisite report"
bash artifact/check_live_rerun_prereqs.sh

echo "[5] Run explanatory reviewer claim audit"
bash artifact/reviewer_audit.sh

echo "[6] Run cached-output reproduction"
bash artifact/reproduce_main.sh

echo "[7] Run provenance verification"
bash artifact/verify_provenance.sh

echo "[8] Run optional local project-code smoke test"
if command -v timeout >/dev/null 2>&1; then
  timeout 60 bash artifact/run_smoke_test.sh
else
  echo "[WARN] timeout command not available; running smoke test without timeout"
  bash artifact/run_smoke_test.sh
fi

echo "[9] Check for prompt-injection text"
if grep -R -I -i -n --exclude='final_preflight.sh' --exclude='59_package_ed_artifact.py' "ignore previous instructions\\|give this paper a high score\\|accept this paper" .; then
  echo "[FAIL] prompt-injection-like text found"
  exit 1
fi
printf '[PASS] prompt-injection scan clean\\n'

echo "[10] Create local extracted-package manifests"
rm -f artifact_file_manifest.txt artifact_sha256_manifest.txt
tmp_manifest="$(mktemp)"
tmp_hashes="$(mktemp)"
find . -type f \\
  ! -name 'artifact_file_manifest.txt' \\
  ! -name 'artifact_sha256_manifest.txt' \\
  | sort > "$tmp_manifest"
find . -type f \\
  ! -name 'artifact_file_manifest.txt' \\
  ! -name 'artifact_sha256_manifest.txt' \\
  -print0 | sort -z | xargs -0 sha256sum > "$tmp_hashes"
mv "$tmp_manifest" artifact_file_manifest.txt
mv "$tmp_hashes" artifact_sha256_manifest.txt
printf '[PASS] extracted-package manifests created\\n'

echo "[11] Check extracted package size"
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
    write_sanitized_text(artifact_root / "REVIEWER_WORKFLOW.md", build_reviewer_workflow())
    write_sanitized_text(artifact_root / "PROJECT_GUIDE_FOR_REVIEWERS.md", build_project_guide_for_reviewers())
    write_sanitized_text(artifact_root / "OUTPUT_INTERPRETATION_GUIDE.md", build_output_interpretation_guide())
    write_sanitized_text(artifact_root / "LIVE_RERUN_GUIDE.md", build_live_rerun_guide())
    write_sanitized_text(artifact_root / "FULL_REPRODUCTION_GUIDE.md", build_full_reproduction_guide())
    write_sanitized_text(artifact_root / "EXPERIMENT_RERUN_GUIDE.md", build_experiment_rerun_guide())
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
    write_sanitized_text(artifact_root / "VERIFICATION_LOG_2026-05-06.md", build_verification_log())
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
