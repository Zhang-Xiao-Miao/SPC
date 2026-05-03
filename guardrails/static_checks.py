from __future__ import annotations

import ast
import re
from typing import Dict, Optional


def expected_return_type(prompt: str) -> Optional[str]:
    lowered = prompt.lower()
    patterns = [
        ("dictionary", "dict"),
        ("dict", "dict"),
        ("list", "list"),
        ("tuple", "tuple"),
        ("set", "set"),
        ("boolean", "bool"),
        ("true or false", "bool"),
        ("float", "float"),
        ("integer", "int"),
        ("string", "str"),
    ]
    for needle, expected in patterns:
        if needle in lowered:
            return expected
    return None


def infer_literal_type(node: ast.AST | None) -> Optional[str]:
    if node is None:
        return None
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Tuple):
        return "tuple"
    if isinstance(node, ast.Dict):
        return "dict"
    if isinstance(node, ast.Set):
        return "set"
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "str"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        name = node.func.id
        if name in {"list", "tuple", "dict", "set", "str", "int", "float", "bool"}:
            return name
    return None


def infer_required_arity(code: str) -> Optional[int]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            positional = [arg.arg for arg in node.args.args]
            defaults = len(node.args.defaults)
            return max(len(positional) - defaults, 0)
    return None


def run_static_checks(code: str, entry_point: str, prompt: str, expected_arity: Optional[int] = None) -> Dict[str, object]:
    result: Dict[str, object] = {
        "parse_ok": False,
        "function_name_ok": False,
        "arity_ok": expected_arity is None,
        "return_type_ok": True,
        "first_function_name": None,
        "detected_arity": None,
        "detected_return_type": None,
    }
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        result["parse_error"] = str(exc)
        return result
    result["parse_ok"] = True
    function = next((node for node in tree.body if isinstance(node, ast.FunctionDef)), None)
    if function is None:
        return result
    result["first_function_name"] = function.name
    result["function_name_ok"] = function.name == entry_point
    positional = [arg.arg for arg in function.args.args]
    defaults = len(function.args.defaults)
    detected_arity = max(len(positional) - defaults, 0)
    result["detected_arity"] = detected_arity
    if expected_arity is not None:
        result["arity_ok"] = detected_arity == expected_arity
    return_types = [infer_literal_type(node.value) for node in ast.walk(function) if isinstance(node, ast.Return)]
    return_types = [value for value in return_types if value is not None]
    detected_return_type = return_types[0] if return_types else None
    result["detected_return_type"] = detected_return_type
    expected_type = expected_return_type(prompt)
    if expected_type and detected_return_type:
        result["return_type_ok"] = detected_return_type == expected_type
    return result
