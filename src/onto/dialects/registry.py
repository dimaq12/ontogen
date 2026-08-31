# -*- coding: utf-8 -*-
"""Registry of dialects: data, not branching. Adding a dialect = adding a line."""
from __future__ import annotations

import importlib

_DIALECTS = {
    "go-stdlib": "onto.dialects.go_stdlib",
    "python-stdlib": "onto.dialects.python_stdlib",
    "kotlin-stdlib": "onto.dialects.kotlin_stdlib",
    "rust-stdlib": "onto.dialects.rust_stdlib",
}


def names() -> list[str]:
    return sorted(_DIALECTS)


def get(name: str) -> dict:
    if name not in _DIALECTS:
        raise KeyError(f"unknown dialect '{name}' (available: {names()})")
    pkg = _DIALECTS[name]
    return {
        "skeleton": importlib.import_module(pkg + ".skeleton"),
        "gates": importlib.import_module(pkg + ".gates"),
    }
