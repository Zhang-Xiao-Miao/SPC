from __future__ import annotations

import ast
import warnings
from collections import Counter
from typing import Any, Dict, List

from plan_b.schema import StructureSummary


CONTROL_FLOW = (ast.For, ast.While, ast.If, ast.Try, ast.With, ast.Break, ast.Continue)
DATA_STRUCTURES = {
    ast.List: "list",
    ast.Dict: "dict",
    ast.Set: "set",
    ast.Tuple: "tuple",
    ast.ListComp: "listcomp",
    ast.DictComp: "dictcomp",
    ast.SetComp: "setcomp",
}


class SkeletonVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.nodes: List[str] = []

    def generic_visit(self, node: ast.AST) -> None:
        important = (
            ast.FunctionDef,
            ast.For,
            ast.While,
            ast.If,
            ast.Return,
            ast.Assign,
            ast.Call,
            ast.ListComp,
            ast.DictComp,
            ast.SetComp,
        )
        if isinstance(node, important):
            self.nodes.append(type(node).__name__)
        super().generic_visit(node)


def _extract_api_calls(tree: ast.AST) -> List[str]:
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return sorted(set(calls))


def _extract_control_flow(tree: ast.AST) -> List[str]:
    tags = [type(node).__name__.lower() for node in ast.walk(tree) if isinstance(node, CONTROL_FLOW)]
    return sorted(set(tags))


def _extract_data_structures(tree: ast.AST) -> List[str]:
    tags = [name for node_type, name in DATA_STRUCTURES.items() for node in ast.walk(tree) if isinstance(node, node_type)]
    return sorted(set(tags))


def _extract_signature(tree: ast.AST) -> Dict[str, Any]:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return {
                "name": node.name,
                "num_args": len(node.args.args),
                "has_vararg": node.args.vararg is not None,
                "returns_annotation": ast.unparse(node.returns) if node.returns is not None else None,
            }
    return {"name": None, "num_args": 0, "has_vararg": False, "returns_annotation": None}


def extract_structure(code: str) -> StructureSummary:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(code)
    except SyntaxError:
        return StructureSummary([], [], [], [], {"name": None, "num_args": 0})
    visitor = SkeletonVisitor()
    visitor.visit(tree)
    return StructureSummary(
        ast_skeleton=visitor.nodes[:24],
        api_calls=_extract_api_calls(tree),
        control_flow=_extract_control_flow(tree),
        data_structures=_extract_data_structures(tree),
        signature=_extract_signature(tree),
    )


def summarize_support_structures(codes: List[str]) -> Dict[str, Counter]:
    counts = {
        "ast_skeleton": Counter(),
        "api_calls": Counter(),
        "control_flow": Counter(),
        "data_structures": Counter(),
    }
    for code in codes:
        summary = extract_structure(code)
        counts["ast_skeleton"].update(summary.ast_skeleton)
        counts["api_calls"].update(summary.api_calls)
        counts["control_flow"].update(summary.control_flow)
        counts["data_structures"].update(summary.data_structures)
    return counts
