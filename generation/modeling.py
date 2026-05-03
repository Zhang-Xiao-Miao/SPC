from __future__ import annotations

import ast
import json
import re
import time
import urllib.error
import urllib.request
import warnings
from dataclasses import dataclass
from typing import List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from plan_b.schema import Example, GenerationCandidate, PriorCandidate


def build_prompt(query: Example, supports: List[Example], prior: Optional[PriorCandidate]) -> str:
    parts = [
        "You are a Python code generator.",
        "Return only Python code.",
    ]
    if prior is not None:
        parts.append("Structural hints:")
        parts.extend(format_prior_lines(prior))
        parts.append("Use these hints as soft guidance, not as hard constraints.")
    for support in supports:
        parts.append("### Example Prompt")
        parts.append(support.prompt.strip())
        parts.append("### Example Solution")
        parts.append(support.code.strip())
    parts.append("### Task")
    parts.append(query.prompt.strip())
    parts.append(f"Implement function `{query.entry_point}`.")
    parts.append("### Solution")
    return "\n".join(parts)


def format_prior_lines(prior: PriorCandidate) -> List[str]:
    summary = prior.summary
    lines = []
    is_oracle = prior.name == "oracle"
    signature = summary.get("signature", {})
    num_args = signature.get("num_args")
    if num_args is not None:
        prefix = "ground-truth" if is_oracle else "likely"
        lines.append(f"- {prefix} function arity: {num_args}")
    api_calls = summary.get("api_calls", [])
    if api_calls:
        prefix = "ground-truth" if is_oracle else "likely"
        lines.append(f"- {prefix} api calls: {', '.join(api_calls[:6])}")
    control_flow = summary.get("control_flow", [])
    if control_flow:
        prefix = "ground-truth" if is_oracle else "likely"
        lines.append(f"- {prefix} control flow: {', '.join(control_flow[:6])}")
    data_structures = summary.get("data_structures", [])
    if data_structures:
        prefix = "ground-truth" if is_oracle else "likely"
        lines.append(f"- {prefix} data structures: {', '.join(data_structures[:6])}")
    algorithm_plan = summary.get("algorithm_plan", [])
    if algorithm_plan:
        prefix = "ground-truth" if is_oracle else "candidate"
        lines.append(f"- {prefix} algorithm plan:")
        lines.extend(f"  {index}. {step}" for index, step in enumerate(algorithm_plan[:8], start=1))
    ast_skeleton = summary.get("ast_skeleton", [])
    if ast_skeleton and not is_oracle and not algorithm_plan:
        lines.append(f"- coarse syntax pattern: {' -> '.join(ast_skeleton[:8])}")
    if not lines:
        lines.append("- no reliable structural hints")
    return lines


def _extract_first_function_block(text: str) -> str:
    fenced = re.findall(r"```(?:python)?\n(.*?)```", text, flags=re.S)
    if fenced:
        text = fenced[0]
    lines = text.strip().splitlines()
    if not lines:
        return text.strip()
    start = 0
    for index, line in enumerate(lines):
        if line.startswith("def ") or line.startswith("import ") or line.startswith("from "):
            start = index
            break
    return "\n".join(lines[start:]).strip()


@dataclass
class LocalGenerator:
    generator_name: str
    model_name: Optional[str] = None
    device: str = "cpu"
    max_new_tokens: int = 192
    api_base: Optional[str] = None

    def __post_init__(self) -> None:
        self.tokenizer = None
        self.model = None
        self._vllm_use_completions = False
        if self.generator_name == "hf_causal" and self.model_name:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()

    def generate(self, query: Example, supports: List[Example], prior: Optional[PriorCandidate], num_samples: int = 1, temperature: float = 0.2) -> List[GenerationCandidate]:
        if self.generator_name == "hf_causal" and self.model is not None and self.tokenizer is not None:
            return self._generate_with_hf(query, supports, prior, num_samples=num_samples, temperature=temperature)
        if self.generator_name == "vllm_openai" and self.model_name and self.api_base:
            return self._generate_with_vllm(query, supports, prior, num_samples=num_samples, temperature=temperature)
        return self._generate_with_exemplar_edit(query, supports, prior, num_samples=num_samples)

    def _generate_with_exemplar_edit(self, query: Example, supports: List[Example], prior: Optional[PriorCandidate], num_samples: int) -> List[GenerationCandidate]:
        candidates = []
        support = supports[0] if supports else None
        base_code = support.code if support is not None else f"def {query.entry_point}(*args, **kwargs):\n    raise NotImplementedError\n"
        code = rename_first_function(base_code, query.entry_point)
        if not code.strip().startswith("def "):
            code = f"def {query.entry_point}(*args, **kwargs):\n    raise NotImplementedError\n"
        for index in range(num_samples):
            candidates.append(
                GenerationCandidate(
                    code=code,
                    source="retrieval_edit",
                    prior_name=prior.name if prior is not None else None,
                    score=1.0 / (index + 1),
                    details={"latency_sec": 0.0, "prompt_tokens": 0, "completion_tokens": 0},
                )
            )
        return candidates

    def _generate_with_hf(self, query: Example, supports: List[Example], prior: Optional[PriorCandidate], num_samples: int, temperature: float) -> List[GenerationCandidate]:
        prompt = build_prompt(query, supports, prior)
        tokens = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_len = tokens["input_ids"].shape[1]
        started = time.monotonic()
        outputs = self.model.generate(
            **tokens,
            do_sample=True,
            num_return_sequences=num_samples,
            temperature=temperature,
            top_p=0.95,
            max_new_tokens=self.max_new_tokens,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        latency_sec = time.monotonic() - started
        candidates = []
        for output in outputs:
            new_tokens = output[input_len:]
            decoded = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
            code = _extract_first_function_block(decoded)
            if "### Task" in code:
                code = code.split("### Task", 1)[0].strip()
            if not code:
                code = f"def {query.entry_point}(*args, **kwargs):\n    raise NotImplementedError\n"
            candidates.append(
                GenerationCandidate(
                    code=code,
                    source=self.model_name or "hf_causal",
                    prior_name=prior.name if prior is not None else None,
                    score=0.0,
                    details={
                        "latency_sec": latency_sec / max(num_samples, 1),
                        "prompt_tokens": int(input_len),
                        "completion_tokens": int(new_tokens.shape[0]),
                    },
                )
            )
        return candidates

    def _generate_with_vllm(self, query: Example, supports: List[Example], prior: Optional[PriorCandidate], num_samples: int, temperature: float) -> List[GenerationCandidate]:
        prompt = build_prompt(query, supports, prior)
        chat_payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a Python code generator. Return only Python code."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": self.max_new_tokens,
            "n": num_samples,
        }
        completion_payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": self.max_new_tokens,
            "n": num_samples,
        }
        if self._vllm_use_completions:
            api_mode = "completions"
            started = time.monotonic()
            raw = self._post_vllm_json("completions", completion_payload)
            choice_texts = [choice.get("text", "") for choice in raw.get("choices", [])]
        else:
            api_mode = "chat"
            started = time.monotonic()
            try:
                raw = self._post_vllm_json("chat/completions", chat_payload)
                choice_texts = [choice.get("message", {}).get("content", "") for choice in raw.get("choices", [])]
            except urllib.error.HTTPError as error:
                body = error.read().decode("utf-8", errors="replace")
                if error.code != 400 or "chat template" not in body:
                    raise RuntimeError(f"vLLM chat request failed with HTTP {error.code}: {body}") from error
                self._vllm_use_completions = True
                api_mode = "completions"
                started = time.monotonic()
                raw = self._post_vllm_json("completions", completion_payload)
                choice_texts = [choice.get("text", "") for choice in raw.get("choices", [])]
        latency_sec = time.monotonic() - started
        usage = raw.get("usage", {})
        prompt_tokens = int(usage.get("prompt_tokens", 0))
        total_completion_tokens = int(usage.get("completion_tokens", 0))
        candidates = []
        for content in choice_texts:
            code = _extract_first_function_block(content)
            if "### Task" in code:
                code = code.split("### Task", 1)[0].strip()
            if not code:
                code = f"def {query.entry_point}(*args, **kwargs):\n    raise NotImplementedError\n"
            candidates.append(
                GenerationCandidate(
                    code=code,
                    source=self.model_name,
                    prior_name=prior.name if prior is not None else None,
                    score=0.0,
                    details={
                        "latency_sec": latency_sec / max(len(choice_texts), 1),
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": total_completion_tokens // max(len(choice_texts), 1),
                        "api_mode": api_mode,
                    },
                )
            )
        return candidates

    def _post_vllm_json(self, path: str, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{self.api_base.rstrip('/')}/{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))


def rename_first_function(code: str, new_name: str) -> str:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(code)
    except SyntaxError:
        return code
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            node.name = new_name
            break
    return ast.unparse(tree)
