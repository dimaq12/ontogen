# -*- coding: utf-8 -*-
"""Linters for the project's invariants (SPEC §1, NOT.md). A violation = a build error.

F0 exam: these linters MUST go red on planted violations
(tests/test_lint.py — the linter itself is checked first, then the code by it).

I1  (NOT §1–2):  the core (core/) knows no phenotype languages; `if dialect` is forbidden.
I4  (NOT §4):    extra=allow (pydantic) is forbidden throughout the engine.
ST2 (NOT §31):   machine-specific paths are forbidden throughout the engine.
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    rule: str
    path: str
    line: int
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: [{self.rule}] {self.text.strip()[:90]}"


# I1: markers of phenotype languages/tissues, forbidden in core/. Not "python" —
# the engine itself is written in it; what's forbidden are FOREIGN tissues and their artifacts.
_I1_CORE = [
    (re.compile(r'\.go["\']|\bgolang\b|\bgofmt\b|\bgo vet\b|\bgo test\b|\bgo build\b'), "Go in core"),
    (re.compile(r'\.rs["\']|\brustc\b|\bcargo\b'), "Rust in core"),
    (re.compile(r'\bfastapi\b|\bgin\b(?!g)|\baxum\b'), "phenotype framework in core"),
    (re.compile(r'\bif\s+.*\bdialect\b\s*(==|!=|\.startswith)'), "branching on dialect"),
    (re.compile(r'\bJinja|jinja2\b'), "phenotype templating in core (printing belongs to dialects)"),
]
# The whole engine:
_ENGINE_WIDE = [
    (re.compile(r'extra\s*=\s*["\']allow["\']'), "extra=allow (NOT §4: hub-IR is typed)"),  # lint: allow
    (re.compile(r'["\'](?:/home/|/tmp/claude|/Users/)'), "machine-specific path (NOT §31)"),
]

_SKIP_DIRS = {".venv", "__pycache__", ".git", ".pytest_cache", "spikes"}


def _iter_py(root: pathlib.Path):
    for p in sorted(root.rglob("*.py")):
        if not any(part in _SKIP_DIRS for part in p.parts):
            yield p


def check_file(path: pathlib.Path, *, is_core: bool, root: pathlib.Path | None = None) -> list[Violation]:
    rel = str(path.relative_to(root)) if root else str(path)
    out: list[Violation] = []
    rules = list(_ENGINE_WIDE) + (list(_I1_CORE) if is_core else [])
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "lint: allow" in line:          # an explicit, visible exception
            continue
        for rx, why in rules:
            if rx.search(line):
                out.append(Violation("I1" if (rx, why) in _I1_CORE else "ENG", rel, i, f"{why}: {line}"))
    return out


def check_tree(src_root: pathlib.Path) -> list[Violation]:
    """src_root = the src/onto directory. core/ is checked more strictly (I1)."""
    out: list[Violation] = []
    for p in _iter_py(src_root):
        is_core = "core" in p.relative_to(src_root).parts
        out.extend(check_file(p, is_core=is_core, root=src_root.parent.parent))
    return out


def main(argv: list[str] | None = None) -> int:
    import sys
    root = pathlib.Path(argv[0]) if argv else pathlib.Path(__file__).resolve().parents[1] / "onto"
    vs = check_tree(root)
    for v in vs:
        print(v, file=sys.stderr)
    print(f"onto-lint: {'CLEAN' if not vs else f'{len(vs)} violation(s)'}")
    return 1 if vs else 0
