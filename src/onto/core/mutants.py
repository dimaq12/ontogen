# -*- coding: utf-8 -*-
"""Mutants — transformations of the reference's Expr AST (SPEC §9.3): court
calibration.

Each mutant must be DISTINGUISHED from the reference by the court (prove_equiv
yields a counterexample) OR caught by a contract (prove_rule yields a
counterexample). A mutant indistinguishable through both channels is a find: a
dead branch in the reference or a hole in the contract; it is reported, not
swept under the rug (NOT: no silent caps).
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

from onto.core import expr as E

_CMP_FLIP = {ast.GtE: ast.Gt, ast.Gt: ast.GtE, ast.LtE: ast.Lt, ast.Lt: ast.LtE}
_ARITH_SWAP = {ast.Add: ast.Sub, ast.Sub: ast.Add}


@dataclass(frozen=True)
class Mutant:
    name: str                 # mutation class
    guard: str | None
    body: str


def _unparse_expr(tree: ast.Expression) -> str:
    return ast.unparse(tree)


def _flip_compares(tree):
    """All variants: one comparison at a time."""
    out = []
    nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)
             and type(n.ops[0]) in _CMP_FLIP]
    for i, _ in enumerate(nodes):
        import copy
        t2 = copy.deepcopy(tree)
        n2 = [n for n in ast.walk(t2) if isinstance(n, ast.Compare)
              and type(n.ops[0]) in _CMP_FLIP][i]
        n2.ops[0] = _CMP_FLIP[type(n2.ops[0])]()
        out.append(t2)
    return out


def generate(guard_src: str | None, body_src: str) -> list[Mutant]:
    muts: list[Mutant] = []
    body = E.parse_body(body_src)

    # 1. drop the guard (clamp) entirely
    if guard_src:
        muts.append(Mutant("drop-guard", None, body_src))
        # 2. weaken a comparison in the guard (>= -> >, etc.)
        for t2 in _flip_compares(E.parse_expr(guard_src)):
            muts.append(Mutant("flip-guard-cmp", _unparse_expr(t2), body_src))

    # 3. swap +/- in the body's increments (one at a time)
    import copy
    assigns = [n for n in ast.walk(body) if isinstance(n, ast.BinOp)
               and type(n.op) in _ARITH_SWAP]
    for i, _ in enumerate(assigns):
        b2 = copy.deepcopy(body)
        n2 = [n for n in ast.walk(b2) if isinstance(n, ast.BinOp)
              and type(n.op) in _ARITH_SWAP][i]
        n2.op = _ARITH_SWAP[type(n2.op)]()
        muts.append(Mutant("swap-arith", guard_src, ast.unparse(b2)))

    # 4. double the body's integer constants (1 -> 2)
    consts = [n for n in ast.walk(body) if isinstance(n, ast.Constant)
              and isinstance(n.value, int) and not isinstance(n.value, bool)
              and n.value != 0]
    for i, _ in enumerate(consts):
        b2 = copy.deepcopy(body)
        n2 = [n for n in ast.walk(b2) if isinstance(n, ast.Constant)
              and isinstance(n.value, int) and not isinstance(n.value, bool)
              and n.value != 0][i]
        n2.value = n2.value * 2
        muts.append(Mutant("double-const", guard_src, ast.unparse(b2)))

    # 5. kill the if branch in the body (then-only)
    ifs = [n for n in ast.walk(body) if isinstance(n, ast.If)]
    for i, _ in enumerate(ifs):
        b2 = copy.deepcopy(body)
        n2 = [n for n in ast.walk(b2) if isinstance(n, ast.If)][i]
        n2.test = ast.copy_location(ast.Constant(value=True), n2.test)
        muts.append(Mutant("kill-branch", guard_src, ast.unparse(b2)))

    # dedup by (guard, body)
    seen, out = set(), []
    for m in muts:
        k = (m.guard, m.body)
        if k not in seen and (m.guard, m.body) != (guard_src, body_src):
            seen.add(k)
            out.append(m)
    return out
