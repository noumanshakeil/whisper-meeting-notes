"""Built-in tools for agent demos."""
from __future__ import annotations

import ast
import operator as op
from pathlib import Path

import httpx

SAFE_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPS:
        return SAFE_OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPS:
        return SAFE_OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsafe expression")

def calculator(expr: str) -> str:
    tree = ast.parse(expr, mode="eval")
    return str(_eval(tree.body))

def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return "FILE_NOT_FOUND"
    return p.read_text(encoding="utf-8")[:4000]

def http_get(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "INVALID_URL"
    try:
        r = httpx.get(url, timeout=10, follow_redirects=True)
        return r.text[:2000]
    except Exception as e:
        return f"ERROR: {e}"

TOOLS = {
    "calculator": calculator,
    "read_file": read_file,
    "http_get": http_get,
}
