from __future__ import annotations

import argparse
import importlib.util
import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path


REVIEW_FILES = [
    "README.md",
    "artifact/REVIEWER_WORKFLOW.md",
    "artifact/FULL_REPRODUCTION_GUIDE.md",
    "artifact/reviewer_audit.sh",
    "artifact/reproduce_main.sh",
    "artifact/verify_provenance.sh",
    "scripts/70_reviewer_claim_audit.py",
]

LIVE_DATA_FILES = [
    "data/processed/mbpp/train.jsonl",
    "data/processed/mbpp/test.jsonl",
    "data/raw/evalplus/MbppPlus.jsonl.gz",
    "data/raw/evalplus/HumanEvalPlus.jsonl.gz",
    "data/processed/evalplus/mbppplus_test.jsonl",
    "data/processed/evalplus/humanevalplus_test.jsonl",
    "data/episodes/mbppplus_test224_episodes.jsonl",
    "data/episodes/mbppplus_test100_episodes.jsonl",
    "data/episodes/mbppplus_test224_prompt_structural_episodes.jsonl",
    "data/episodes/humanevalplus_test50_syntax_episodes.jsonl",
]

LIVE_MODULES = [
    "datasets",
    "openai",
    "torch",
    "transformers",
    "vllm",
    "yaml",
]

ENDPOINTS = [
    ("Qwen main", "http://127.0.0.1:8000/v1/models"),
    ("DeepSeek boundary", "http://127.0.0.1:8001/v1/models"),
    ("StarCoder2 boundary", "http://127.0.0.1:8002/v1/models"),
    ("Granite boundary", "http://127.0.0.1:8003/v1/models"),
]


def exists(path: str) -> bool:
    return Path(path).exists()


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def endpoint_status(url: str, timeout: float) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            text = response.read(5000).decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
            model_count = len(payload.get("data", [])) if isinstance(payload, dict) else "unknown"
            return True, f"reachable, models={model_count}"
        except json.JSONDecodeError:
            return True, "reachable, non-JSON response"
    except urllib.error.URLError as exc:
        return False, f"not reachable ({exc.reason})"
    except socket.timeout:
        return False, "not reachable (timeout)"
    except Exception as exc:
        return False, f"not reachable ({exc})"


def print_rows(title: str, rows: list[tuple[str, bool, str]], missing_label: str = "MISSING") -> bool:
    print()
    print(title)
    print("-" * len(title))
    ok = True
    for label, passed, detail in rows:
        mark = "OK" if passed else missing_label
        print(f"[{mark:16s}] {label}: {detail}")
        ok = ok and passed
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Check prerequisites for default review commands and optional live reruns.")
    parser.add_argument("--strict-live", action="store_true", help="Exit non-zero if live-rerun prerequisites are missing.")
    parser.add_argument("--check-endpoints", action="store_true", help="Probe local vLLM/OpenAI-compatible endpoints.")
    parser.add_argument("--endpoint-timeout", type=float, default=2.0)
    args = parser.parse_args()

    print("SPC-Audit live-rerun prerequisite check")
    print(f"Python: {sys.version.split()[0]}")
    print()
    print("This report is for OPTIONAL full live LLM reruns only.")
    print("Missing items below do not affect the default reviewer audit.")
    print("The default audit uses cached outputs and should be run with:")
    print("  bash artifact/reviewer_audit.sh")
    print("  bash artifact/reproduce_main.sh")
    print("  bash artifact/verify_provenance.sh")

    review_rows = [(path, exists(path), path) for path in REVIEW_FILES]
    review_ok = print_rows("Default reviewer-audit files", review_rows)

    print()
    print("The following items are required only for optional live LLM reruns.")
    print("They are not needed for the default reviewer audit path.")

    live_data_rows = [(path, exists(path), path) for path in LIVE_DATA_FILES]
    live_data_ok = print_rows("Live-rerun data files", live_data_rows, missing_label="OPTIONAL-LIVE-MISSING")

    module_rows = [(name, module_available(name), name) for name in LIVE_MODULES]
    module_ok = print_rows("Optional live-rerun Python modules", module_rows, missing_label="OPTIONAL-LIVE-MISSING")

    endpoint_ok = True
    if args.check_endpoints:
        endpoint_rows = []
        for label, url in ENDPOINTS:
            ok, detail = endpoint_status(url, args.endpoint_timeout)
            endpoint_rows.append((label, ok, detail))
        endpoint_ok = print_rows("Optional local model endpoints", endpoint_rows, missing_label="OPTIONAL-LIVE-MISSING")
    else:
        print()
        print("Optional local model endpoints")
        print("------------------------------")
        print("[SKIPPED] endpoint probing disabled; pass --check-endpoints to test /v1/models URLs")

    print()
    print("Interpretation")
    print("--------------")
    if review_ok:
        print("- Default artifact review is ready: reviewer_audit/reproduce_main/verify_provenance can run from packaged files.")
    else:
        print("- Default artifact review is incomplete. Re-extract the archive or inspect missing files above.")
    if live_data_ok and module_ok and (endpoint_ok or not args.check_endpoints):
        print("- Live rerun prerequisites look mostly ready. Follow artifact/FULL_REPRODUCTION_GUIDE.md.")
    else:
        print("- Optional full live reruns are not ready yet. Install missing optional modules, reconstruct data files, and start model endpoints.")
    print("- Missing live-rerun prerequisites do not invalidate cached-output audit; they only block raw LLM regeneration.")

    if args.strict_live and not (live_data_ok and module_ok and endpoint_ok):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
