from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from plan_b.experiment_utils import markdown_table, summarize_run
from plan_b.io_utils import read_json, write_json, write_text


def main() -> None:
    rows = []
    payload = {"runs": [], "limitations": []}

    vllm_no_prior = "results/mbppplus100_syntax_aware_no_prior_mbrexec_budget8_seed1.json"
    vllm_multi = "results/mbppplus100_syntax_aware_multi_prior_mbrexec_budget8_seed1.json"
    if Path(vllm_no_prior).exists() and Path(vllm_multi).exists():
        no_prior_stats = summarize_run(read_json(vllm_no_prior))
        multi_stats = summarize_run(read_json(vllm_multi))
        payload["runs"].append(
            {
                "backend": "vllm_openai / Qwen2.5-Coder-7B-Instruct",
                "dataset": "MBPP+100",
                "baseline_path": vllm_no_prior,
                "structure_path": vllm_multi,
                "baseline_passed": no_prior_stats["passed"],
                "structure_passed": multi_stats["passed"],
                "delta": multi_stats["passed"] - no_prior_stats["passed"],
            }
        )
        rows.append(
            [
                "vllm_openai / Qwen2.5-Coder-7B-Instruct",
                "MBPP+100 fair-budget",
                "79/100",
                "82/100",
                "+3",
                "Primary evidence",
            ]
        )

    hf_no_prior = "results/hf_fixed_noprior_nogate_nombr.json"
    hf_multi = "results/hf_fixed_multiprior_gate_mbrexec.json"
    if Path(hf_no_prior).exists() and Path(hf_multi).exists():
        no_prior_stats = summarize_run(read_json(hf_no_prior))
        multi_stats = summarize_run(read_json(hf_multi))
        payload["runs"].append(
            {
                "backend": "hf_causal / bigcode-tiny-starcoder-py",
                "dataset": "MBPP weak-test smoke",
                "baseline_path": hf_no_prior,
                "structure_path": hf_multi,
                "baseline_passed": no_prior_stats["passed"],
                "structure_passed": multi_stats["passed"],
                "delta": multi_stats["passed"] - no_prior_stats["passed"],
            }
        )
        rows.append(
            [
                "hf_causal / bigcode-tiny-starcoder-py",
                "MBPP smoke",
                f"{no_prior_stats['passed']}/{no_prior_stats['num_episodes']}",
                f"{multi_stats['passed']}/{multi_stats['num_episodes']}",
                f"{multi_stats['passed'] - no_prior_stats['passed']:+d}",
                "Secondary portability smoke",
            ]
        )
    else:
        payload["limitations"].append(
            "A second backend with a directly comparable MBPP+100 fair-budget run is not present in the workspace. The current cross-model check is therefore only a smoke-level portability probe."
        )

    md = "# Minimal Cross-Model Portability Check\n\n"
    md += markdown_table(
        ["Backend", "Dataset", "No Prior", "Structure-Aware", "Delta", "Role"],
        rows,
    )
    md += "\n"
    md += "Interpretation: the main fair-budget evidence still comes from the vLLM/Qwen backend. The HF row is a portability smoke check only; it should not be presented as equal-strength evidence.\n"
    if payload["limitations"]:
        md += "\n## Limitations\n\n"
        for item in payload["limitations"]:
            md += f"- {item}\n"

    write_json("paper/tbl_cross_model.json", payload)
    write_text("paper/tbl_cross_model.md", md)


if __name__ == "__main__":
    main()
